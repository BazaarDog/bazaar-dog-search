from datetime import timedelta
import logging
import operator

from django.db.models import Q, Prefetch, Count
from django.utils.timezone import now

from ob.models.listing import Listing
from ob.models.shipping_options import ShippingOptions
from ob.api.serializer import *
from ob.api.filter import *
from ob.api.query.common import check_peer, get_nsfw_filter_queryset

logger = logging.getLogger(__name__)


def get_queryset(self):

    check_peer(self.request.query_params)

    dust_param = [True, False] if \
        self.request.query_params.get('dust') == 'true' else [False]

    a_week_ago = now() - timedelta(days=7)
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

    currencies = self.request.query_params.getlist('acceptedCurrencies')
    if currencies:
        cq_list = [Q(accepted_currencies__contains=[c]) for c in currencies]
        queryset = queryset.filter(reduce(operator.or_, cq_list))

    shipping = self.request.query_params.get('shipping')
    if shipping:
        queryset = queryset.filter(
            Q(shippingoptions__regions__icontains=shipping) |
            Q(shippingoptions__regions__icontains='ALL') |
            Q(shippingoptions__regions__isnull=True))

    if self.request.query_params.get('free_shipping_region') == 'true':
        c = self.request.query_params.get('shipping') or 'ALL'
        queryset = queryset.filter(contract_type=Listing.PHYSICAL_GOOD).filter(
            Q(free_shipping__icontains=c) |
            Q(free_shipping__icontains='ALL') |
            Q(shippingoptions__regions__isnull=True))

    nsfw = self.request.query_params.get('nsfw')
    queryset = get_nsfw_filter_queryset(queryset, nsfw)

    return queryset

