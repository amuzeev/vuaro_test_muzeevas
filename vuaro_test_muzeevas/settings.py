# -*- coding: utf-8 -*-

from conf.development import *
from conf.celery_conf import *
from conf.email import *

INSTALLED_APPS += (
    'rest_framework',
    'rest_framework_swagger',
    'celery',
    'thumbnailfield',

    'vuaro_test_muzeevas.apps.gallery'
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'vuaro_test_muzeevas.apps.context_processors.users',
)

MIDDLEWARE_CLASSES += (
    'vuaro_test_muzeevas.apps.middleware.LoginRequiredMiddleware',

)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vuaro_muzeevas',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}


SWAGGER_SETTINGS = {
    "exclude_namespaces": [], # List URL namespaces to ignore
    "api_version": '1',  # Specify your API's version
    "api_path": "/",  # Specify the path to your API not a root level
    "enabled_methods": [  # Specify which methods to enable in Swagger UI
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    "api_key": '', # An API key
    "is_authenticated": False,  # Set to True to enforce user authentication,
    "is_superuser": False,  # Set to True to enforce admin only access
}
