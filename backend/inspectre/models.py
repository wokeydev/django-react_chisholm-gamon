from django.db import models
from .settings import INSPECTRE_BASE_URL
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting
class InspectRealEstateSettings(BaseSetting):
    inspect_real_estate_agentid = models.CharField(max_length=50, blank=True, default="",
                                                   help_text="IRE agentID to integrate with their system")
    inspect_real_estate_base_url = models.CharField(max_length=255, default=INSPECTRE_BASE_URL)
