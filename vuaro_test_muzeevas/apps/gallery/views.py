# -*- coding: utf-8 -*-
import os
import zipfile

from annoying.decorators import ajax_request

from django.forms import modelformset_factory
from django.conf import settings

from django.core.urlresolvers import reverse
from django.core.files.uploadhandler import TemporaryUploadedFile, InMemoryUploadedFile
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from django.views.generic import ListView, TemplateView, DeleteView
from django.shortcuts import get_object_or_404, redirect

from .models import Picture
from .forms import PictureForm
from .tasks import async_save_in_memory, async_save_temporary, send_pictures_by_email


class PictureView(ListView):
    model = Picture
    template_name = "pictures.html"
    context_object_name = 'pictures8'

    def get(self, request, *args, **kwargs):

        user = self.request.user
        if 'user_pk' in self.kwargs:
            user = get_object_or_404(User, pk=self.kwargs['user_pk'])

        self.object_list = self.get_queryset().filter(owner=user).filter(image_processed=True)

        context = self.get_context_data()
        context.update({
            'my': request.user == user,
            'gallery_user': user,
            'pictures_count': self.object_list.count()
        })
        return self.render_to_response(context)


class UploadView(TemplateView):
    template_name = 'upload.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)


def upload_files(request):
    files = request.FILES.getlist('images')

    for image_file in files:
        if image_file.content_type not in [u'image/jpeg', u'image/gif', u'image/pjpeg', u'image/png']:
            continue

        instance = Picture.objects.create(owner=request.user)

        data = {}
        file_info = []

        if image_file.__class__ is InMemoryUploadedFile:

            file_info.append(image_file.field_name)
            file_info.append(image_file.name)
            file_info.append(image_file.content_type)
            file_info.append(image_file.size)
            file_info.append(image_file.charset)

            #the actual data of the image, read into a string
            data['data'] = image_file.read()

            async_save_in_memory.delay(data, file_info, instance.pk)
        else:
            storage = FileSystemStorage()
            path = storage.save(u'uploaded/%s' % image_file.name, image_file)

            async_save_temporary.delay(instance.pk, path, image_file.name)

    return redirect(reverse('my_picture'))


class DeletePictureView(TemplateView):
    template_name = 'delete.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        formset_kwargs = {
            'queryset': Picture.objects.filter(owner=request.user)
        }

        PictureFormSet = modelformset_factory(Picture, fields=('image',), can_delete=True, extra=0)
        formset = PictureFormSet(**formset_kwargs)

        context['formset'] = formset

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        formset_kwargs = {
            'queryset': Picture.objects.filter(owner=request.user)
        }
        PictureFormSet = modelformset_factory(Picture, fields=('image',), can_delete=True, extra=0)
        formset = PictureFormSet(request.POST,  **formset_kwargs)

        if formset.is_valid():
            formset.save()

            formset = PictureFormSet(**formset_kwargs)

        context['formset'] = formset

        return self.render_to_response(context)


def create_zip_archive(user):
    zip_file_name = u'picture_archive_%s.zip' % user.username
    path_zip_file = os.path.join(settings.BASE_DIR, '..', 'zips', zip_file_name)

    paths_zip_file = []
    paths_zip_file.append(path_zip_file)
    pictures = user.my_pictures.all()

    paths = [picture.image.path for picture in pictures]

    # with zipfile.ZipFile(path_zip_file, 'w') as zipf:
    #     for path in paths:
    #         zipf.write(path, os.path.basename(path))

    max_size = settings.EMAIL_ATTACH_MAX_SIZE
    archive_num = 0
    zipf = zipfile.ZipFile(path_zip_file, 'w')

    for path in paths:
        file_size = os.path.getsize(path)
        zipf_size =  zipf.fp.tell()
        if file_size + zipf_size >= max_size:
            zipf.close()
            archive_num += 1
            zip_file_name = u'picture_archive_%s_%d.zip' % (user.username, archive_num)
            path_zip_file = os.path.join(settings.BASE_DIR, '..', 'zips', zip_file_name)
            paths_zip_file.append(path_zip_file)
            zipf = zipfile.ZipFile(path_zip_file, 'w')

        zipf.write(path, os.path.basename(path))

    return paths_zip_file


@csrf_exempt
@ajax_request
def send_email(request):
    if not request.is_ajax():
        return HttpResponseBadRequest()

    paths_zip_file = create_zip_archive(request.user)
    send_pictures_by_email.delay(paths_zip_file, request.user.email)

    return {'status': 'success'}