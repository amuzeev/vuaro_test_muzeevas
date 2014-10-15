# -*- coding: utf-8 -*-

import celery
import os
import StringIO
import pika

from django.core.cache import cache
from django.core.files.uploadedfile import InMemoryUploadedFile, File
from django.core.mail import EmailMessage
from django.conf import settings

from .models import Picture


parameters = pika.ConnectionParameters(
    host='localhost',
    port=5672
)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()
channel.queue_declare(queue='completed', durable=True)


def send_to_rabbitmq(picture):
    message = {
        'event_type': 'new_image',
        'picture_id': picture.id,
        'picture_image_url': picture.image.url,
        'picture_image_small_url': picture.image.small.url
    }

    msg = {
        'user_id': str(picture.owner_id),
        'body': message
    }

    channel.basic_publish('', 'completed', str(msg))


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

    send_to_rabbitmq(picture)

@celery.task(track_started=True, default_retry_delay=30)
def async_save_temporary(pk, path, filename):
    picture = Picture.objects.get(pk=pk)
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    with open(full_path) as f:
        picture.image.save(filename, File(f))

    picture.image_processed = True
    picture.save()
    picture.image.small

    send_to_rabbitmq(picture)

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