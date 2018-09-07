from django.contrib import admin
from .models import OfficePage, OfficeGroup


@admin.register(OfficePage)
class OfficePageAdmin(admin.ModelAdmin):
    pass


@admin.register(OfficeGroup)
class OfficeGroupAdmin(admin.ModelAdmin):
    pass
