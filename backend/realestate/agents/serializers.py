from rest_framework import serializers
from .models import AgentPage
from wagtail.wagtailimages.api.fields import ImageRenditionField


class AgentPageSerializer(serializers.ModelSerializer):
    results_image = ImageRenditionField('fill-150x176', source='profile_image')

    class Meta:
        model = AgentPage
        fields = (
            'id',
            'title',
            'name_short',
            'job_title',
            'phone',
            'office_phone',
            'email',
            'full_url',
            'results_image'
        )
