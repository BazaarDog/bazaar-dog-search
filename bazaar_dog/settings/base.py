from django.utils.translation import ugettext_lazy as _

import os
import random
import string


def get_random_str(str_len):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(str_len))


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = get_random_str(80)


# This is a non-standard variable to make some bells turn on and off, not much danger.
DEV = False

# WARNING: don't run with debug turned on in production!
DEBUG = False  # Rather than change this setting, it is recommended to override it in a child config

ONION = False

OB_API_USER = os.getenv('OB_API_USER')
OB_API_PASSWORD = os.getenv('OB_API_PASSWORD')

OB_API_AUTH = (OB_API_USER, OB_API_PASSWORD)

CRAWL_TIMEOUT = 128  # seconds
SHORTEST_UPDATE_HOURS = 3  # don't hit nodes more than once every X hours

OB_USE_SSL = os.getenv('OB_USE_SSL', 'True')
DEFAULT_CERT_PATH = '/home/' + os.getenv('USER') + '/.openbazaar/ssl/OpenBazaar.crt'
OB_CERTIFICATE = os.getenv('OB_CERTIFICATE', DEFAULT_CERT_PATH)

# Don't use ssl if explicitly set not to.
if OB_USE_SSL == 'False':
    OB_PROTOCOL = 'http://'
else:
    OB_PROTOCOL = 'https://'

OB_SERVER = os.getenv('OB_SERVER', '127.0.0.1')
OB_SERVER_MAINNET_PORT = os.getenv('OB_SERVER_MAINNET_PORT', '4002')
OB_SERVER_TESTNET_PORT = os.getenv('OB_SERVER_TESTNET_PORT', '4102')

OB_MAINNET_ENDPOINT = OB_PROTOCOL + OB_SERVER + ':' + OB_SERVER_MAINNET_PORT
OB_TESTNET_ENDPOINT = OB_PROTOCOL + OB_SERVER + ':' + OB_SERVER_TESTNET_PORT

IPNS_MAINNET_HOST = OB_MAINNET_ENDPOINT + "/ipns/"
IPNS_TESTNET_HOST = OB_TESTNET_ENDPOINT + '/ipns/'

OB_MAINNET_HOST = OB_MAINNET_ENDPOINT + '/ob/'
OB_TESTNET_HOST = OB_TESTNET_ENDPOINT + '/ob/'

DUST_FEE_PERCENT = 2

APPEND_SLASH = True

SITE_NAME = 'Bazaar Dog'

# the openbazaar client won't work with straight ip addresses, therefore
# it may be helpful to configure a dns record for development purposes,
# (against a domain you own and control).
SITE_URL = 'http://admin.bazaar.dog'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'admin.bazaar.dog', ]

# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'ob',
]

# Since we do not utilize users or logging in, authentication is disabled,
# for now.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'ob.middleware.ForceCORS',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ob.middleware.HumanizeMiddleware',
]

ROOT_URLCONF = 'bazaar_dog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bazaar_dog.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'PAGINATE_BY_PARAM': 'count',
    'ORDERING_PARAM': 'sortBy',
    'URL_FORMAT_OVERRIDE': 'json',
    'SEARCH_PARAM': 'q',
}

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

# This will not work without a fair amount of modification
# Performance and reliability are not great with sqlite either
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


# Postgres to get array field support
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.getenv('DATABASE_HOST'),
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'PORT': os.getenv('DATABASE_PORT'),
    },
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/


LOCALE_PATHS = (
    os.path.join(BASE_DIR, '../locale'),
)

LANGUAGE_CODE = 'en-us'

LANGUAGES = [
    ('ar', _('Arabic')),
    ('da', _('Danish')),
    ('de', _('German')),
    ('en', _('English')),
    ('es', _('Spanish')),
    ('fr', _('French')),
    ('it', _('Italian')),
    ('ja', _('Japanese')),
    ('ko', _('Korean')),
    ('nl', _('Dutch')),
    ('pt', _('Portuguese')),
    ('ru', _('Russian')),
    ('zh-hans', _('Simplified Chinese')),
    ('zh-hant', _('Traditional Chinese')),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

# not used
STATIC_URL = '/static/'
