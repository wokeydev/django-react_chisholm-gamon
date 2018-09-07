from django.contrib.sitemaps import Sitemap
from .models import PropertyListing
from .enums import STATUS_CURRENT, STATUS_SOLD


class PropertySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return PropertyListing.objects.filter(
            status__in=[STATUS_CURRENT, STATUS_SOLD]
        )

    def lastmod(self, obj):
        return obj.updated
