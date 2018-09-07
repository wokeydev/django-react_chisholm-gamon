"""
General CMS applicable Field blocks
"""

from django.conf import settings
from collections import OrderedDict
from rest_framework import serializers
from wagtail.images.models import SourceImageIOError
from wagtail.images.api.fields import ImageRenditionField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core.blocks import PageChooserBlock

# Custom Image chooser block that works inside streamfields


class ImageSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        self.filter_spec = kwargs.pop('filter_spec')
        super().__init__(*args, **kwargs)

    def to_representation(self, image):
        try:
            thumbnail = image.get_rendition(self.filter_spec)

            return OrderedDict([
                ('url', thumbnail.url),
                ('width', thumbnail.width),
                ('height', thumbnail.height),
            ])
        except SourceImageIOError:
            return OrderedDict([
                ('error', 'SourceImageIOError'),
            ])


class APIImageChooserBlock(ImageChooserBlock):
    def get_api_representation(self, value, context=None):
        data = ImageSerializer(filter_spec='original').to_representation(value)
        if 'url' in data:
            data['url'] = ''.join([
                settings.SITE_DOMAIN,
                data['url']
            ])
        return data


class AbsoluteImageRenditionField(ImageRenditionField):
    # Custom Image rendition field that apprents the full path to the URL
    def to_representation(self, image):
        rep = super().to_representation(image)
        if 'url' in rep:
            rep['url'] = ''.join([
                settings.SITE_DOMAIN,
                rep['url']
            ])
        return rep


class DetailedPageChooserBlock(PageChooserBlock):
    # Custom PageChooserBlock to bring back more details in the API
    def get_api_representation(self, value, context=None):
        try:
            return {
                'slug': value.slug,
                'id': value.pk,
                'title': value.title,
                'path': value.get_url(),
                'type': type(value)._meta.app_label + '.' + type(value).__name__
            }
        except AttributeError:
            return super().get_api_representation(value, context=context)
