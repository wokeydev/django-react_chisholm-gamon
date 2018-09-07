from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks
from .models import SuburbData


class SuburbDataModelAdmin(ModelAdmin):
    model = SuburbData
    menu_label = 'Suburbs'
    menu_icon = 'fa-map-marker'
    list_display = ('name', 'state_code', 'postcode')
    search_fields = ('name', 'state_code')
    add_to_settings_menu = True


modeladmin_register(SuburbDataModelAdmin)
