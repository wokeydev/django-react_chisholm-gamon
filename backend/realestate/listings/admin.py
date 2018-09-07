from django.contrib import admin
from .models import PropertyListing

# Register your models here.
@admin.register(PropertyListing)
class PropertyListingAdmin(admin.ModelAdmin):
    pass
