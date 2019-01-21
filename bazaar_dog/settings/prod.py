import os
from .base import *

DEBUG = False

SITE_NAME = 'Bazaar Dog'
SITE_URL = 'https://bazaar.dog'

ALLOWED_HOSTS = ['bazaar.dog']

API_GATEWAY_HOST = os.getenv('API_GATEWAY_HOST')

if API_GATEWAY_HOST:
    ALLOWED_HOSTS += [API_GATEWAY_HOST]

# Postgres is highly recommended
# DATABASES = {
#     'default': {
#     'ENGINE': 'django.db.backends.postgresql_psycopg2',
#     'HOST': os.getenv('DATABASE_HOST'),
#     'NAME': os.getenv('DATABASE_NAME'),
#     'USER': os.getenv('DATABASE_USER'),
#     'PASSWORD': os.getenv('DATABASE_PASSWORD'),
#     'PORT': os.getenv('DATABASE_PORT'),
#     },
# }
#
