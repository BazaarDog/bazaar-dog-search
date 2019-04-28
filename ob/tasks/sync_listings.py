import json
import logging
from requests.exceptions import ConnectionError, ReadTimeout

from django.conf import settings

from ob.models.listing import Listing
from ob.models.exchange_rate import ExchangeRate
from ob.models.util import get

logger = logging.getLogger(__name__)
OB_HOST = settings.OB_MAINNET_HOST


def sync_listings(profile):
    listing_url = OB_HOST + 'listings/' + profile.peerID

    try:
        from ob.tasks.sync_listing import sync_listing as sync_listing_deep
        response = get(listing_url)
        if response.status_code == 200:
            try:
                for data in json.loads(response.content.decode('utf-8')):
                    listing = sync_listing_fast(data, profile)
                    listing.save()
                    sync_listing_deep(listing)

            except json.decoder.JSONDecodeError:
                logger.info(
                    "Problem decoding json for listings of peer: " +
                    profile.peerID
                )
        else:
            code = response.status_code
            logger.debug('{} fetching {}'.format(code, listing_url))

    except (ReadTimeout, ConnectionError):
        logger.info("listing peerID " + profile.peerID + " timeout")


def sync_listing_fast(listing_data, profile):
    # logger.info(profile.peerID + ': ' + listing_data['slug'])
    l, listing_created = Listing.objects.get_or_create(
        profile=profile,
        slug=listing_data.get('slug')
    )

    if listing_created:
        l.hash = listing_data.get('hash')
        l.title = listing_data.get('title')
        l.description = listing_data.get('description')
        l.rating_average_stale = listing_data.get('averageRating')
        l.rating_count_stale = listing_data.get('ratingCount')
        l.free_shipping = listing_data.get('freeShipping')
        l.active = True
        l.network = 'mainnet'

        # Don't override manual nsfw data
        if l.listingreport_set.count() == 0:
            l.nsfw = listing_data.get('nsfw')

        l.price, l.pricing_currency, l.price_value = get_price(
            listing_data.get('price')
        )

        l.contract_type = get_contract_type(listing_data.get('contractType'))

    else:
        l.rating_average_stale = listing_data.get('averageRating')
        l.rating_count_stale = listing_data.get('ratingCount')
        l.free_shipping = listing_data.get('freeShipping')
        l.active = True
    return l


def get_contract_type(contract_type):
    if contract_type:
        if hasattr(Listing, contract_type) and \
                isinstance(
                    getattr(Listing, contract_type),
                    int
                ):
            return getattr(Listing, contract_type)


def get_price(price_data):
    price, pricing_currency, price_value = 0, 0, 0
    if price_data:
        price = price_data.get('amount')
        pricing_currency = price_data.get('currencyCode')
        c, fx_created = ExchangeRate.objects.get_or_create(
            symbol=pricing_currency)
        if fx_created:
            from ob.util import get_exchange_rates
            get_exchange_rates()
        price_value = get_price_value(price, c)

    return price, pricing_currency, price_value


def get_price_value(price, c):
    try:
        return price / float(c.base_unit) / float(c.rate)
    except ZeroDivisionError:
        return 0.0001
