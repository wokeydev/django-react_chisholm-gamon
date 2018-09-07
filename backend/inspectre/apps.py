from django.apps import AppConfig


class InspectreConfig(AppConfig):
    """
    Application to integrate with the "Inspect Real Estate" platform.
    Primary usage is a template tag that accepts a realestate.listings.PropertyListing
    instance and returns a valid IRE link.
    Also includes a wagtail site settings for setting the IRE ID.
    """
    name = 'inspectre'
