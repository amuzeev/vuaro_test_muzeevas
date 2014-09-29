# -*- coding: utf-8 -*-

import celery
import os
import StringIO

from django.core.cache import cache
from django.core.files.uploadedfile import InMemoryUploadedFile, File
from django.core.mail import EmailMessage
from django.conf import settings



from .models import Picture

@celery.task(track_started=True, default_retry_delay=30)
def async_save_in_memory(data, file_info, pk):
    picture = Picture.objects.get(pk=pk)

    img = StringIO.StringIO(data['data'])
    image = InMemoryUploadedFile(img, *file_info)
    picture.image = image

    picture.image_processed = True
    picture.save()
    picture.image.small

    cache.clear()

@celery.task(track_started=True, default_retry_delay=30)
def async_save_temporary(pk, path, filename):
    picture = Picture.objects.get(pk=pk)
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    with open(full_path) as f:
        picture.image.save(filename, File(f))

    picture.image_processed = True
    picture.save()
    picture.image.small

    os.remove(full_path)



@celery.task(track_started=True, default_retry_delay=30)
def send_pictures_by_email(paths_zip_file, to):
    for filename in paths_zip_file:
        message = EmailMessage(
            subject=u'My pictures',
            body=u'Archive of my pictures',
            to=[to]
        )
        message.attach_file(filename)
        message.send()

    if len(paths_zip_file) > 1:
        return u'%d Messages sended to %s' % (len(paths_zip_file), to)

    return u'Message sended to %s' % to