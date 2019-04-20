import os
from .base import *

DEBUG = False

SITE_NAME = 'Bazaar Dog'
SITE_URL = 'https://bazaar.dog'

ALLOWED_HOSTS = ['bazaar.dog']

API_GATEWAY_HOST = os.getenv('API_GATEWAY_HOST')

if API_GATEWAY_HOST:
    ALLOWED_HOSTS += [API_GATEWAY_HOST]
