from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks
from .models import School


class SchoolModelAdmin(ModelAdmin):
    model = School
    menu_label = 'Schools'
    menu_icon = 'fa-university'
    list_display = ('name', 'suburb', 'school_level', 'school_type')
    search_fields = ('suburb', 'name')


modeladmin_register(SchoolModelAdmin)
