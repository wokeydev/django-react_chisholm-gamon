from rest_framework import serializers
from .models import PropertyListing


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyListing
        fields = '__all__'
