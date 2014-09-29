# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin


from .views import (PictureView, UploadView, DeletePictureView,
                    send_email, upload_files)

urlpatterns = patterns('',
    url(r'^my/$', PictureView.as_view(), name='my_picture'),
    url(r'^user/(?P<user_pk>\d+)/$', PictureView.as_view(), name='user_picture'),

    url(r'^upload/$', UploadView.as_view(), name='upload'),
    url(r'^upload_files/$', upload_files, name='upload_files'),

    url(r'^delete/$', DeletePictureView.as_view(), name='delete'),

    url(r'^send_pictures/$', send_email, name='send_email'),

)
