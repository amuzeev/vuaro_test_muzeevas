# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from apps.gallery.api import *

# Проекты
my_picture = MyPictureViewSet.as_view({'get': 'list'})
user_picture = UserPictureViewSet.as_view({'get': 'list'})


urlpatterns = format_suffix_patterns(patterns('',

    url(r'^my/$', my_picture, name='my_picture'),
    url(r'^user/(?P<user_pk>\d+)/$', user_picture, name='user_picture'),

))
