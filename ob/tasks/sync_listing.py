import json
import logging
import requests

from django.conf import settings
from django.dispatch import receiver
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.timezone import now

from ob.util import get
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
            listing_data = data['listing']
            signature = data['signature']
            if listing.signature == signature and force is False:
                listing.save()
            else:
                listing.signature = signature
                listing.slug = listing_data['slug']
                metadata = listing_data['metadata']
                listing.version = metadata['version']
                listing.contract_type = getattr(Listing,
                                                metadata['contractType'])
                listing.accepted_currencies = metadata.get(
                    'acceptedCurrencies')
                listing.pricing_currency = metadata.get('pricingCurrency')

                item_details = listing_data.get('item')
                listing.title = item_details.get('title')
                listing.tags = item_details.get('tags')
                listing.categories = item_details.get('categories')

                listing.price = item_details.get('price')
                listing.price_value = get_price_value(listing.price,
                                                      listing.pricing_currency)

                listing.description = item_details.get('description')

                if item_details['condition']:
                    listing.condition_type = getattr(Listing,
                                                     item_details[
                                                         'condition'].upper())

                for i, iHashes in enumerate(item_details.get('images')):
                    iHashes['index'] = i
                    iHashes['listing'] = listing
                    li, li_c = ListingImage.objects.get_or_create(
                        **iHashes)
                    li.save()

                mod_data = listing_data.get('moderators')
                if mod_data:
                    moderator_list = get_moderators(mod_data)
                    listing.moderators.set(moderator_list)

                for so in listing_data.get('shippingOptions'):
                    s = ShippingOptions.create_from_json(listing, so)
                    s.save()

                listing.network = 'mainnet'
                listing.save()
        else:
            logger.debug('Error: {}'.format(r.status_code))

    except json.decoder.JSONDecodeError:
        logger.debug("bad json")
    except requests.exceptions.ReadTimeout:
        is_modified = Listing.objects.filter(slug=listing.slug,
                                             profile=listing.profile).update(
            attempt=now())
        logger.debug("timeout")


def get_price_value(listing_price, listing_pricing_currency):
    try:
        c = ExchangeRate.objects.get(symbol=listing_pricing_currency)
        return listing_price / float(
            c.base_unit) / float(c.rate)
    except ZeroDivisionError:
        return 0.0001


def get_moderators(listed_moderators):
    known_moderators = Profile.objects.filter(pk__in=listed_moderators)
    known_moderators_pks = [m.pk for m in known_moderators]
    new_moderators = [m for m in listed_moderators if
                      m not in known_moderators_pks]
    if len(new_moderators) > 0:
        for new_pk in new_moderators:
            try:
                Profile.objects.get(pk=new_pk)
            except Profile.DoesNotExist:
                new_mod, m_created = Profile.objects.get_or_create(
                    pk=new_pk)
                if m_created:
                    from ob.tasks.sync_profile import sync_profile
                    sync_profile(new_mod)

        moderators = Profile.objects.filter(
            pk__in=listed_moderators)
    else:
        moderators = known_moderators

    return list(moderators)
