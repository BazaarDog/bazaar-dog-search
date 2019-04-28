import logging
import requests

from django.conf import settings
from pathlib import Path

logger = logging.getLogger(__name__)


class ObNodeSSLError(Exception):
    pass


def get(url, timeout=settings.CRAWL_TIMEOUT):
    if 'https' in url:
        if Path(settings.OB_CERTIFICATE).is_file():
            return requests.get(url,
                                timeout=timeout,
                                auth=settings.OB_API_AUTH,
                                verify=settings.OB_CERTIFICATE)
        else:
            raise ObNodeSSLError("couldn't find ssl cert for a secure "
                                 "connection to openbazaar-go server... ")
    else:
        return requests.get(url, timeout=settings.CRAWL_TIMEOUT)
