import json
import logging
import requests

from django.conf import settings
from django.db.models import F, Count
from django.utils.timezone import now

from ob.bootstrap.known_nodes import peerId_list
from ob.models.profile import Profile
from ob.models.listing import Listing
from ob.models.exchange_rate import ExchangeRate

from pathlib import Path

logger = logging.getLogger(__name__)


def bootstrap():
    for peerId in peerId_list:
        p, pc = Profile.objects.get_or_create(pk=peerId)
        if p.should_update():
            try:
                p.sync(testnet=False)
            except requests.exceptions.ReadTimeout:
                logger.info("read timeout")
        else:
            logger.info('skipping profile')


def get_exchange_rates():
    rates_url = settings.OB_MAINNET_HOST + 'exchangerates/BCH'
    response = requests.get(rates_url,
                            timeout=settings.CRAWL_TIMEOUT,
                            auth=settings.OB_API_AUTH,
                            verify=settings.OB_CERTIFICATE
                            )
    if response.status_code == 200:
        forex_data = json.loads(response.content.decode('utf-8'))
        for symbol, rate in forex_data.items():
            updated = ExchangeRate.objects.filter(symbol__exact=symbol).update(
                rate=rate)
            if updated == 0:
                fx, fx_c = ExchangeRate.objects.get_or_create(symbol=symbol)
                fx.rate = rate
                fx.save()


def update_price_values():
    # Listing.update(stories_filed=F('stories_filed') + 1)
    qs_currency_count = Listing.objects.values('pricing_currency') \
        .annotate(cur_count=Count('pricing_currency')) \
        .filter(cur_count__gte=1).order_by('-cur_count')
    distinct_currencies = [v['pricing_currency'] for v in
                           list(qs_currency_count)]
    for c_symbol in distinct_currencies:
        try:
            c = ExchangeRate.objects.get(symbol=c_symbol)
            if c.rate:
                a = Listing.objects.filter(pricing_currency=c_symbol).update(
                    price_value=F('price') / float(c.base_unit) / float(c.rate))
            else:
                logging.warning("No rate for {}".format(c.symbol))
        except ExchangeRate.DoesNotExist:
            logger.info(
                'could not update price_values of ' + c_symbol + ' listings')


def update_verified(verified_url=None):
    if not verified_url:
        verified_url = 'https://search.ob1.io/verified_moderators'
    response = requests.get(verified_url)
    if response.status_code == 200:
        from ob.models.profile import Profile
        verified_data = json.loads(response.content.decode('utf-8'))
        verified_pks = [p['peerID'] for p in verified_data['moderators']]
        Profile.objects.filter().update(verified=False)
        r = Profile.objects.filter(peerID__in=verified_pks).update(verified=True)
        return r, verified_url
    else:
        logger.error("Error getting verified vendors from ")
