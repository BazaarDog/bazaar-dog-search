import json
import logging
import requests

from django.utils.timezone import now

from ob.models.util import get
from ob.models.listing import Listing
from ob.models.shipping_options import ShippingOptions
from ob.models.profile import Profile
from ob.models.exchange_rate import ExchangeRate
from ob.models.listing_image import ListingImage

logger = logging.getLogger(__name__)


def sync_listing(listing, force=True):
    listing_detail_url = listing.get_sync_url()
    logger.debug(listing.profile_id + " sync : " + listing.slug)
    try:
        r = get(listing_detail_url)
        if r.status_code == 200:
            data = json.loads(r.content.decode('utf-8'))

            parse_listing(listing, data)
        else:
            logger.debug('Error: {}'.format(r.status_code))

    except json.decoder.JSONDecodeError:
        logger.debug("bad json")
    except requests.exceptions.ReadTimeout:
        is_modified = Listing.objects.filter(slug=listing.slug,
                                             profile=listing.profile).update(
            attempt=now())
        logger.debug("timeout")


def parse_listing(listing, data, force=True):
    listing_data = data.get('listing')
    signature = data.get('signature')
    if listing.signature == signature and force is False:
        listing.save()
    else:
        listing.signature = signature
        listing.slug = listing_data.get('slug')
        listing.parse_metadata(listing_data)

        item_details = listing_data.get('item')
        listing.title = item_details.get('title')
        listing.tags = item_details.get('tags')
        listing.categories = item_details.get('categories')

        listing.price = item_details.get('price')
        listing.price_value = get_price_value(listing.price,
                                              listing.pricing_currency)

        listing.description = item_details.get('description')
        listing.condition_type = get_condition_type(
            item_details.get('condition')
        )

        listing.moderators.set(
            get_moderators(
                listing_data.get('moderators')
            )
        )
        create_listing_images(listing, item_details.get('images'))
        create_shipping_options(listing, listing_data.get('shippingOptions'))

        listing.network = 'mainnet'
        listing.save()


def get_price_value(listing_price, listing_pricing_currency):
    try:
        c = ExchangeRate.objects.get(symbol=listing_pricing_currency)
        return listing_price / float(
            c.base_unit) / float(c.rate)
    except ZeroDivisionError:
        return 0.0001


def get_condition_type(condition):
    if condition:
        return getattr(Listing, condition.upper())


def create_listing_images(listing, images):
    for i, iHashes in enumerate(images or []):
        iHashes['index'] = i
        iHashes['listing'] = listing
        li, li_c = ListingImage.objects.get_or_create(
            **iHashes)
        li.save()


def create_shipping_options(listing, shipping_options):
    for so in shipping_options or []:
        s = ShippingOptions.create_from_json(listing, so)
        s.save()


def get_moderators(listed_moderators):
    known_moderators = Profile.objects.filter(pk__in=listed_moderators)
    new_moderators = get_new_moderators(listed_moderators, known_moderators)

    for new_pk in new_moderators or []:
        try_sync_moderator(new_pk)
    if len(new_moderators) > 0:
        known_moderators = Profile.objects.filter(pk__in=listed_moderators)

    return list(known_moderators)


def get_new_moderators(listed_moderators, known_moderators):
    known_moderators_pks = [m.pk for m in known_moderators]
    new_moderators = [m for m in listed_moderators if
                      m not in known_moderators_pks]
    return new_moderators


def try_sync_moderator(new_pk):
    try:
        Profile.objects.get(pk=new_pk)
    except Profile.DoesNotExist:
        new_mod, m_created = Profile.objects.get_or_create(
            pk=new_pk)
        if m_created:
            from ob.tasks.sync_profile import sync_profile
            sync_profile(new_mod)
