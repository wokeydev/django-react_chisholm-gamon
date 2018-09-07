from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.core import hooks
from .models import PropertyListing


class PropertyListingModelAdmin(ModelAdmin):
    model = PropertyListing
    menu_label = 'Properties'
    menu_icon = 'fa-home'
    list_display = ('uniqueID', 'address_full', 'category')
    search_fields = ('address_suburb', 'address_street')

    def register_with_wagtail(self):

        @hooks.register('register_permissions')
        def register_permissions():
            return self.get_permissions_for_registration()

        @hooks.register('register_admin_urls')
        def register_admin_urls():
            return self.get_admin_urls_for_registration()

        menu_hook = 'construct_realestate_menu'

        @hooks.register(menu_hook)
        def register_admin_menu_item(request, menu_items):
            return menu_items.append(self.get_menu_item())

        # Overriding the explorer page queryset is a somewhat 'niche' / experimental
        # operation, so only attach that hook if we specifically opt into it
        # by returning True from will_modify_explorer_page_queryset
        if self.will_modify_explorer_page_queryset():
            @hooks.register('construct_explorer_page_queryset')
            def construct_explorer_page_queryset(parent_page, queryset, request):
                return self.modify_explorer_page_queryset(
                    parent_page, queryset, request)
