from django import template
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
register = template.Library()


@register.simple_tag
def get_setting(val):
    try:
        return getattr(settings, val, "")
    except ValueError:
        return ""


@register.filter
def strip_ptags(val):
    try:
        return val.replace('<p>', '').replace('</p>', '')
    except Exception:
        return val

@register.filter
def just_listed(val):
    created = val
    now = timezone.now()
    oneweekago = now - timedelta(days=7)
    if created > oneweekago:
        return True
    else:
        return False
