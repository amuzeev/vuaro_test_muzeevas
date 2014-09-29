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
            None: ((1280, 1280, 'thumbnail'),),
            'large': ((640, 480, 'thumbnail'),),
            'small': ((400, 400, 'thumbnail'), (200, 200, 'crop', {'left': 0, 'upper': 0})),

            'tiny': (160, 120),
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