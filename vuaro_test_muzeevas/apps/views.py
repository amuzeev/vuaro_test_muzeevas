# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.views import auth_login, auth_logout, get_current_site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.base import View, ContextMixin

from gallery.models import Picture

from .forms import AuthForm, RegForm


class IndexView(TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['pictures'] = Picture.objects.filter(image_processed=True).order_by('-date_created')[:9]
        return context


class LoginView(TemplateView):
    template_name = "registration/login.html"
    auth_form = AuthForm

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        form = self.auth_form(self.request)

        current_site = get_current_site(self.request)

        context.update({
            'auth_form': form,
            'site': current_site,
            'site_name': current_site.name,
        })
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        form = self.auth_form(request, data=request.POST)
        if form.is_valid():

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            return HttpResponseRedirect(reverse('my_picture'))
        #else:
        #    form = self.auth_form(request)

        context.update({
            'auth_form': form
        })

        return self.render_to_response(context)


class LogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponseRedirect(reverse('index'))


class RegistrationView(TemplateView):
    template_name = "registration/registration.html"
    reg_form = RegForm

    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data(**kwargs)
        form = self.reg_form()

        context.update({
            'reg_form': form,
        })
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        form = self.reg_form(data=request.POST)
        if form.is_valid():
            user = form.save()

            auth_login(request, user)

            return HttpResponseRedirect(reverse('my_picture'))

        context.update({
            'reg_form': form,
        })

        return self.render_to_response(context)

#users = User.objects.order_by('username')