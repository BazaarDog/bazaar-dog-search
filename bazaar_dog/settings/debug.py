from .base import *

DEBUG = True
DEV = True

SITE_NAME = 'Bazaar Dog'

SITE_URL = 'http://debug.bazaar.dog'

ALLOWED_HOSTS = ['debug.bazaar.dog', '127.0.0.1', 'localhost']

INTERNAL_IPS = ['debug.bazaar.dog', '127.0.0.1', 'localhost']


INSTALLED_APPS = INSTALLED_APPS + ['django.contrib.staticfiles', 'debug_toolbar']

MIDDLEWARE = [
              'debug_toolbar.middleware.DebugToolbarMiddleware',
              'django.contrib.sessions.middleware.SessionMiddleware',
              'ob.middleware.ForceCORS',
              'django.middleware.locale.LocaleMiddleware',
              'django.middleware.common.CommonMiddleware',
              'django.middleware.common.CommonMiddleware',
              'django.middleware.csrf.CsrfViewMiddleware',
              'django.contrib.messages.middleware.MessageMiddleware',
              'django.middleware.clickjacking.XFrameOptionsMiddleware',
              ]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'PAGINATE_BY_PARAM': 'count',
    'ORDERING_PARAM': 'sortBy',
    'URL_FORMAT_OVERRIDE': 'json',
    'SEARCH_PARAM': 'q',
}


