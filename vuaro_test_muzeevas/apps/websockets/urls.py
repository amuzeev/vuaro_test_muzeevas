# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns

from .vuaro_test_muzeevas.apps.websockets.views import *

urlpatterns = patterns('apps.websockets.views',    
    url(r'^$', RedisView.as_view(), name='red'), 
)