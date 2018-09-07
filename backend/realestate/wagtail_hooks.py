from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
from wagtail.core import hooks
from wagtail.core.models import Page, PageRevision, Site
from wagtail.contrib.modeladmin.options import modeladmin_register

from .offices.models import OfficeIndexPage
from .agents.models import AgentIndexPage
from .listings.modeladmin import PropertyListingModelAdmin


@hooks.register('construct_main_menu')
def create_realestate_menu(request, menu_items):
    re_menu = Menu(register_hook_name='register_realestate_menu_item', construct_hook_name='construct_realestate_menu')
    menu_items.append(
        SubmenuMenuItem(
            _('Real Estate'), re_menu, classnames='icon icon-home', order=10000
        )
    )


@hooks.register('construct_realestate_menu')
def add_office_realestate_menu(request, menu_items):
    # We need office index to exist at the home
    root = Site.objects.latest('pk').root_page

    try:
        office_index = OfficeIndexPage.objects.get()
    except OfficeIndexPage.MultipleObjectsReturned:
        office_index = OfficeIndexPage.objects.first()
    except OfficeIndexPage.DoesNotExist:
        office_index = OfficeIndexPage(
            title='Offices',
            slug='real-estate-offices',
            show_in_menus=True
        )
        root.add_child(instance=office_index)
        revision = PageRevision(
            page=office_index,
            user=None,
            submitted_for_moderation=False,
            content_json={}
        )
        revision.publish()
        office_index.save()

    menu_items.append(
        MenuItem('Offices', reverse('wagtailadmin_explore', args=[office_index.pk]), classnames='icon icon-fa-building')
    )
    return menu_items


@hooks.register('construct_realestate_menu')
def add_agent_realestate_menu(request, menu_items):
    # We need office index to exist at the home
    root = Site.objects.latest('pk').root_page

    try:
        agent_index = AgentIndexPage.objects.get()
    except AgentIndexPage.MultipleObjectsReturned:
        agent_index = AgentIndexPage.objects.first()
    except AgentIndexPage.DoesNotExist:
        agent_index = AgentIndexPage(
            title='Agents',
            slug='real-estate-agents',
            show_in_menus=True
        )
        root.add_child(instance=agent_index)
        revision = PageRevision(
            page=agent_index,
            user=None,
            submitted_for_moderation=False,
            content_json={}
        )
        revision.publish()
        agent_index.save()

    menu_items.append(
        MenuItem('Agents', reverse('wagtailadmin_explore', args=[agent_index.pk]), classnames='icon icon-fa-users')
    )
    return menu_items


@hooks.register('construct_realestate_menu')
def add_testmonial_menus(request, menu_items):
    menu_items.append(
        MenuItem('Testimonials', reverse('wagtailsnippets:list', args=['testimonials', 'testimonial']), classnames='icon icon-fa-comment', order=1000),
    )
    return menu_items


modeladmin_register(PropertyListingModelAdmin)
