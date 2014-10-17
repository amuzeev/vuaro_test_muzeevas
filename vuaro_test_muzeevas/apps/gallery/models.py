# -*- coding: utf-8 -*-

import os

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from pytils.translit import translify
from sorl.thumbnail import ImageField, get_thumbnail


def file_path_picture(instance, filename):
    return os.path.join('pictures', 'thumbnails',  translify(filename).replace(' ', '_'))

upload_to = 'pictures/thumbnails'


class Picture(models.Model):
    date_created = models.DateTimeField(verbose_name=_(u'Дата'), auto_now_add=True)
    owner = models.ForeignKey(to=User, verbose_name=_(u'Владелец'), related_name='my_pictures')

    image = ImageField(_('Изображение'), upload_to=upload_to)
    image_processed = models.BooleanField(verbose_name=_(u'Обработана'), default=False)

    class Meta:
        ordering = ('-date_created',)

    @property
    def image_thumb(self):
        return get_thumbnail(self.image, '200x200', crop='center')

    # def get_notes(self):
    #     return self.notes.filter(user=self.owner)



#
# class Note(models.Model):
#     date_created = models.DateTimeField(verbose_name=_(u'Дата'), auto_now_add=True)
#     date_modified = models.DateTimeField(verbose_name=_(u'Дата'), auto_now=True)
#     user = models.ForeignKey(to=User, verbose_name=_(u'Пользователь'))
#     picture = models.ForeignKey(to=Picture, verbose_name=_(u'Изображение'), related_name='notes')
#     text = models.TextField(verbose_name=_(u'Текст'))