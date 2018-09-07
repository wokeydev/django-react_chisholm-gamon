from django.conf import settings

DEFAULT_PER_PAGE = getattr(settings, "LISTINGS_DEFAULT_PER_PAGE", 12)

try:
    DEFAULT_LISTING_SEARCH_SLUGS = settings.DEFAULT_LISTING_SEARCH_SLUGS
except AttributeError:
    DEFAULT_LISTING_SEARCH_SLUGS = {
        "sale": "buying",
        "rent": "renting",
        "commercial": "commercial-search"
    }
