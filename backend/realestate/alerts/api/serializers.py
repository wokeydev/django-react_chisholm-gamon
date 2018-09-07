from rest_framework import serializers
from ..models import PropertyAlert


class PropertyAlertSerializer(serializers.ModelSerializer):

    class Meta:
        model = PropertyAlert
        fields = (
            'descriptive_name',
            'email',
            'criteria',
            'frequency',
            'unsubscribed',
            'last_sent'
        )
        read_only_fields = ('last_sent',)