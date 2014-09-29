# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from .forms import AuthForm, RegForm


def users(request):
    exclude = {}
    if request.user.is_authenticated():
        exclude.update({'id': request.user.id})

    context = {
        'users': User.objects.order_by('username').exclude(**exclude),
        'auth_form': AuthForm(request, data=request.POST or None),
        'reg_form': RegForm(data=request.POST or None)
    }

    return context
