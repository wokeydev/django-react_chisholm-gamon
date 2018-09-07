from django.contrib.gis import admin
from .models import SuburbData


@admin.register(SuburbData)
class SuburbDataAdmin(admin.GeoModelAdmin):
    list_display = ['name', 'postcode', 'state', 'get_surrounding']
    ordering = ['name']
    search_fields = ['name', 'state_code', 'postcode']

    def get_surrounding(self, obj):
        return ", ".join([str(i) for i in obj.surrounding])
