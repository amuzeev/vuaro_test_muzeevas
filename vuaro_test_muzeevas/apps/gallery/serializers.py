# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import serializers

from .models import Picture


class PictureSerializer(serializers.ModelSerializer):
    """
    id -- ID Изображения
    image_url -- Url изображения
    image_url -- Url превью изображения
    """
    image_url = serializers.Field(source='image.url')
    #image_small_url = serializers.CharField(source='image.small.url')

    class Meta:
        model = Picture
#        fields = ('id', 'image_url', 'image_small_url')
        fields = ('id', 'image_url',)