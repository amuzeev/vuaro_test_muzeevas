# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import status, viewsets, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User

from .models import Picture
from .serializers import PictureSerializer


class PictureViewSet(viewsets.ModelViewSet):
    model = Picture
    serializer_class = PictureSerializer
    allowed_methods = ['GET', 'POST', 'DELETE']
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        qs = super(PictureViewSet, self).get_queryset()
        return qs.filter(image_processed=True)

    def pre_save(self, obj):
        obj.owner = self.request.user


class MyPictureViewSet(PictureViewSet):
    allowed_methods = ['GET']

    def get_queryset(self):
        return super(MyPictureViewSet, self).get_queryset().filter(owner=self.request.user)


class UserPictureViewSet(PictureViewSet):
    allowed_methods = ['GET']
    permission_classes = ()

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs['user_pk'])
        return super(UserPictureViewSet, self).get_queryset().filter(owner=user)
