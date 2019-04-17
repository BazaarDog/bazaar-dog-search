from datetime import timedelta
import logging
from requests.exceptions import ConnectTimeout

from django.db.models import Q, Prefetch, Count
from django.utils.timezone import now

from ob.models import Listing
from ob.api.serializer import *
from ob.api.filter import *
from ob.api.query.common import try_sync_peer

logger = logging.getLogger(__name__)


def get_queryset(self):
    if 'q' in self.request.query_params:
        search_term = self.request.query_params['q']
        if 'Qm' == search_term[:2] and len(search_term) >= 40:
            try_sync_peer(search_term)

    if 'dust' in self.request.query_params and self.request.query_params[
        'dust'] == 'true':
        dust_param = [True, False]
    else:
        dust_param = [False]

    a_week_ago = now() - timedelta(hours=156)
    queryset = Listing.objects \
        .prefetch_related("moderators",
                          Prefetch("images",
                                   queryset=ListingImage.objects.filter(
                                       index=0), to_attr="thumbnail"),
                          Prefetch("profile__avatar",
                                   queryset=Image.objects.filter(),
                                   to_attr="avatar_prefetch")) \
        .select_related('profile') \
        .filter(profile__vendor=True) \
        .filter(profile__was_online__gt=a_week_ago) \
        .exclude(pricing_currency__isnull=True) \
        .exclude(pricing_currency__exact='') \
        .exclude(profile__scam=True) \
        .filter(dust__in=dust_param) \
        .exclude(profile__illegal_in_us=True)
    # .filter(active=True) \ this is redundant with vendor=True

    queryset = queryset.annotate(moderators_count=Count('moderators'))

    if 'shipping' in self.request.query_params:
        c = self.request.query_params['shipping']
        queryset = queryset.filter(
            Q(shippingoptions__regions__icontains=c) |
            Q(shippingoptions__regions__icontains='ALL') |
            Q(shippingoptions__regions__isnull=True))

    if 'free_shipping_region' in self.request.query_params and \
                    self.request.query_params[
                        'free_shipping_region'] == 'true':
        if self.request.query_params['shipping']:
            c = self.request.query_params['shipping']
        else:
            c = 'ALL'
        queryset = queryset.filter(contract_type=Listing.PHYSICAL_GOOD).filter(
            Q(free_shipping__icontains=c) |
            Q(free_shipping__icontains='ALL') |
            Q(shippingoptions__regions__isnull=True))

    if 'nsfw' in self.request.query_params:
        value = self.request.query_params['nsfw']
        # logger.debug('get_query nsfw value is ' + str(value))
        if not value:
            return queryset.exclude(nsfw=True)
        elif value == 'Affirmative':
            return queryset.filter(nsfw=True)
        elif value == 'true' or value is True:
            return queryset
        else:
            return queryset.exclude(nsfw=True)
    else:
        return queryset.exclude(nsfw=True)
