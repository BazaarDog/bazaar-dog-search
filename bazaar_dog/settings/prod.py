from .base import *

DEBUG = False


SITE_NAME = 'Bazaar Dog'
SITE_URL = 'https://bazaar.dog'

ALLOWED_HOSTS = ['bazaar.dog',]

API_GATEWAY_HOST = os.environ.get('API_GATEWAY_HOST')

if API_GATEWAY_HOST:
    ALLOWED_HOSTS += [API_GATEWAY_HOST]

DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'HOST': os.environ.get('DATABASE_HOST'),
    'NAME': os.environ.get('DATABASE_NAME'),
    'USER': os.environ.get('DATABASE_USER'),
    'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
    'PORT': os.environ.get('DATABASE_PORT'),
    },
}

