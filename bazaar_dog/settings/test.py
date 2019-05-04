from .base import *

# This is to speed up tests (possibly), not that passwords are ever used
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
