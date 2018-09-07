from django.conf import settings

INSPECTRE_BASE_URL = getattr(settings, 'INSPECTRE_BASE_URL', "https://book.inspectrealestate.com.au/Register")
