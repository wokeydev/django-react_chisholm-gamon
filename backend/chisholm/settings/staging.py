from .base import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

DEBUG = True

ALLOWED_HOSTS = [
    '0.0.0.0',
    'localhost',
    '*'
]

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.elasticsearch5',
        'URLS': ['http://elasticsearch5:9200'],
        'INDEX': 'wagtail',
        'TIMEOUT': 5,
        'OPTIONS': {},
        'INDEX_SETTINGS': {},
    }
}

MAIL_RECIPIENT_OVERRIDE = [
    'Andy Harris <andy@techequipt.com.au>',
    'Jason Havenaar <jason@techequipt.com.au>',
]

SITE_DOMAIN = 'http://chisholm-api.techequipt.com.au/'

try:
    from .local import *  # noqa
except ModuleNotFoundError:
    pass
