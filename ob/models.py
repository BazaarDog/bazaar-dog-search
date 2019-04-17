from datetime import timedelta
import ipaddress
import json
import logging
import os
from random import randint
import requests
from lxml import etree as lxmletree

from django.conf import settings
from django.db import models
from django.db.models import Count, Sum, Avg, F
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField

from django.dispatch import receiver

from urllib3.exceptions import SubjectAltNameWarning

logger = logging.getLogger(__name__)

requests.packages.urllib3.disable_warnings(SubjectAltNameWarning)

OB_HOST = settings.OB_MAINNET_HOST
IPNS_HOST = settings.IPNS_MAINNET_HOST
OB_INFO_URL = OB_HOST + 'peerinfo/'

try:
    from obscure import get_listing_rank, get_profile_rank
except ImportError:
    from custom import get_listing_rank, get_profile_rank


def try_assign(key, data):
    if key in data.keys():
        return data[key]










