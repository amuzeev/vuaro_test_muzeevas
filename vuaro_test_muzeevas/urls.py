# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static


from apps.gallery.urls import urlpatterns as gallery_urls
from apps.views import IndexView, LoginView, LogoutView, RegistrationView

urlpatterns = patterns('',



    url(r'^$', IndexView.as_view(), name='index'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^registration/$', RegistrationView.as_view(), name='registration'),


    url(r'^api/v1/', include('vuaro_test_muzeevas.urls_api')),
    url(r'^about/api/', include('rest_framework_swagger.urls')),

)

urlpatterns += gallery_urls

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     urlpatterns += patterns('',
#         url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
#             'document_root': settings.MEDIA_ROOT,
#         }),
#         url('^static/(?P<path>.*)$', 'django.views.static.serve', {
#             'document_root': settings.STATIC_ROOT
#         }),
#     )