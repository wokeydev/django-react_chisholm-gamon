from django.contrib import admin
from .models import ListingEnquiry


@admin.register(ListingEnquiry)
class ListingEnquiryAdmin(admin.ModelAdmin):
    list_display = ['listing', 'email_address', 'timestamp']
