"""
Context processor to insert the search listing form on all pages outside the CMS
"""
from .forms import ListingSearchForm
from .settings import DEFAULT_LISTING_SEARCH_SLUGS
from wagtail.core.models import Page


def search_listing_form(request):
    return {'listing_search_form': ListingSearchForm(request.GET)}


def search_pages(request):
    urls = {}
    for name, slug in DEFAULT_LISTING_SEARCH_SLUGS.items():
        try:
            urls[name] = Page.objects.get(slug=slug).full_url
        except Page.DoesNotExist:
            pass

    return {'search_urls': {**urls}}
