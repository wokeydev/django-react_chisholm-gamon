from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import ListingEnquiry
from ..listings.models import PropertyListing


class ListingEnquirySerializer(serializers.ModelSerializer):
    listing = serializers.PrimaryKeyRelatedField(queryset=PropertyListing.objects.all())
    sent_by_user = serializers.PrimaryKeyRelatedField(required=False, queryset=get_user_model().objects.all())

    class Meta:
        model = ListingEnquiry
        fields = '__all__'

    def create(self, validated_data):
        return ListingEnquiry.objects.create(**validated_data)
