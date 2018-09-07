from django import template
from ..models import InspectRealEstateSettings
register = template.Library()


@register.inclusion_tag('inspectre/ire_link.html', takes_context=True)
def ire_link(context, listing):
    return {
        "ire_settings": InspectRealEstateSettings.for_site(context['request'].site),
        "listing": listing
    }
