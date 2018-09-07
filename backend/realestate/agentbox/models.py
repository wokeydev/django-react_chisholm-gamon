from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting


# Settings
@register_setting
class AgentBoxSettings(BaseSetting):
    api_key = models.CharField(max_length=255, blank=True, default="")
    client_id = models.CharField(max_length=255, blank=True, default="")
    staff_webdisplay = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="webDisplay type from AgentBox to expect for public profiles. If not supplied will use all"
    )


class AgentBoxUpdateMeta(models.Model):
    """
    For storing last updated time for import scripts
    """
    last_updated_listings = models.DateTimeField(null=True, default=None)
    last_updated_offices = models.DateTimeField(null=True, default=None)
    last_updated_staff = models.DateTimeField(null=True, default=None)
    last_updated_lookups = models.DateTimeField(null=True, default=None)

    def save(self, **kwargs):
        # We are only allowing a single record - so we check and drop
        if not self.pk and AgentBoxUpdateMeta.objects.all().exists():
            # Already exists
            raise Exception('Only one AgentBoxUpdateMeta can exist')
        super().save()
