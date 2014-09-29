# -*- coding: utf-8 -*-

import os

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from pytils.translit import translify
from thumbnailfield.fields import ThumbnailField


def file_path_picture(instance, filename):
    return os.path.join('pictures', 'thumbnails',  translify(filename).replace(' ', '_'))

upload_to = 'pictures/thumbnails'


class Picture(models.Model):
    date_created = models.DateTimeField(verbose_name=_(u'Дата'), auto_now_add=True)
    owner = models.ForeignKey(to=User, verbose_name=_(u'Владелец'), related_name='my_pictures')

    image = ThumbnailField(_('Изображение'), upload_to=upload_to, patterns={
        # Pattern Format:
        #   <Name>: (
        #   (<square_size>,),       # with defautl process_method
        #   (<width>, <height>,),   # with default process_method
        #   (<width>, <height>, <method or method_name>),
        #   (<width>, <height>, <method or method_name>, <method options>),
        #   )
        #
        # If Name is ``None`` that mean original image will be processed
        # with the pattern
        #
        # Convert original image to sepia and resize it to 800x400 (original
        # size is 804x762)
        None: ((1280, 1280, 'thumbnail'),),
        # Create 640x480 resized thumbnail as large.
        'large': ((640, 480, 'thumbnail'),),
        # Create 320x240 cropped thumbnail as small. You can write short
        # pattern if the number of appling pattern is 1
        'small': (200, 200, 'crop', {'left': 0, 'upper': 0}),
        # Create 160x120 thumbnail as tiny (use default process_method to
        # generate)
        'tiny': (160, 120),
        #
        # These thumbnails are not generated while accessed. These can be
        # accessed with the follwoing code::
        #
        #   entry.thumbnail.large
        #   entry.thumbnail.small
        #   entry.thumbnail.tiny
        #
        #   # shortcut properties
        #   entry.thumbnail.large_file  # as entry.thumbnail.large.file
        #   entry.thumbnail.large_path  # as entry.thumbnail.large.path
        #   entry.thumbnail.large_url   # as entry.thumbnail.large.url
        #   entry.thumbnail.large.size  # as entry.thumbnail.large.size
        #
    },
    blank=True, null=True
    )
    image_processed = models.BooleanField(verbose_name=_(u'Обработана'), default=False)


    def get_notes(self):
        return self.notes.filter(user=self.owner)

#
# class Note(models.Model):
#     date_created = models.DateTimeField(verbose_name=_(u'Дата'), auto_now_add=True)
#     date_modified = models.DateTimeField(verbose_name=_(u'Дата'), auto_now=True)
#     user = models.ForeignKey(to=User, verbose_name=_(u'Пользователь'))
#     picture = models.ForeignKey(to=Picture, verbose_name=_(u'Изображение'), related_name='notes')
#     text = models.TextField(verbose_name=_(u'Текст'))