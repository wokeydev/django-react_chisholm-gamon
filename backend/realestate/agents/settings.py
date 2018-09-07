from django.conf import settings

DEFAULT_AGENTS_PER_PAGE = 50
AGENTS_PER_PAGE = getattr(settings, 'AGENTS_PER_PAGE', DEFAULT_AGENTS_PER_PAGE)
