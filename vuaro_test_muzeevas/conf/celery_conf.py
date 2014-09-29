# -*- coding: utf-8 -*-

from kombu import Queue, Exchange

BROKER_URL = 'amqp://guest:guest@localhost:5672//'

BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 43200}

CELERYD_POOL_RESTARTS = True

CELERY_ACKS_LATE = True

CELERY_TIMEZONE = 'Europe/Moscow'

CELERYD_MAX_TASKS_PER_CHILD = 1


CELERY_RESULT_PERSISTENT = True

CELERY_RESULT_BACKEND = 'amqp'
CELERY_TASK_RESULT_EXPIRES = 3600 * 24 * 7  # 1 week


# Custom settings
QUEUE_PICTURE = 'picture'
QUEUE_DEFAULT = 'default'
QUEUE_EMAIL = 'email'


CELERY_CREATE_MISSING_QUEUES = True

# имена воркеров. прописывают парметром '-n'
DEFAULT_WORKER_NAME = 'celery@default'


CELERY_DEFAULT_QUEUE = QUEUE_DEFAULT
CELERY_DEFAULT_ROUTING_KEY = QUEUE_DEFAULT

CELERY_QUEUES = (
    Queue(name=QUEUE_DEFAULT, routing_key=QUEUE_DEFAULT, exchange=Exchange(QUEUE_DEFAULT)),
    Queue(name=QUEUE_PICTURE, routing_key=QUEUE_PICTURE, exchange=Exchange(QUEUE_PICTURE)),
    Queue(name=QUEUE_EMAIL, routing_key=QUEUE_EMAIL, exchange=Exchange(QUEUE_EMAIL)),
)


CELERY_ROUTES = (
    {'apps.gallery.tasks.async_save_in_memory': {
        'queue': QUEUE_PICTURE,
        'routing_key': QUEUE_PICTURE
    }
    },
    {'apps.gallery.tasks.async_save_temporary': {
        'queue': QUEUE_PICTURE,
        'routing_key': QUEUE_PICTURE
    }
    },
    {'apps.gallery.tasks.send_pictures_by_email': {
        'queue': QUEUE_EMAIL,
        'routing_key': QUEUE_EMAIL
    }
    },




)