from .base import *  # noqa

DEBUG = False
EMAIL_CC = "info@chisholmgamon.com.au"
EMAIL_BCC = "techequipt.logs@gmail.com"

ALLOWED_HOSTS = [
    'www.chisholmgamon.com.au',
]

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '127.0.0.1:6379',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
CACHE_MIDDLEWARE_KEY_PREFIX = 'mpc_'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, '../templates')],
    'OPTIONS': {
        'loaders': [
            ('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]),
        ],
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'wagtailmenus.context_processors.wagtailmenus',
            'wagtail.contrib.settings.context_processors.settings',
            'realestate.listings.context_processors.search_listing_form',
            'realestate.listings.context_processors.search_pages'
        ],
    },
}]

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.elasticsearch5',
        'URLS': ['http://localhost:9200'],
        'INDEX': 'wagtail',
        'TIMEOUT': 5,
        'OPTIONS': {},
        'INDEX_SETTINGS': {},
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'chisholmgamon',
        'USER': 'chisholmgamon',
        'PASSWORD': 'qWHr89+=G*74',
        'HOST': 'localhost',
        # 'PORT': 5432,
    }
}

STATIC_ROOT = os.path.join(PROJECT_DIR, 'static-live')
# We are moving static root due to a ManifestStaticFilesStorage issue with duplicating files.
