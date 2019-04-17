import json
import logging
import requests

from django.conf import settings
from django.dispatch import receiver
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.timezone import now

from ob.util import get
from ob.models import Listing, ShippingOptions, Profile, ExchangeRate, \
    ListingImage

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
                listing.accepted_currencies = metadata[
                    'acceptedCurrencies']
                listing.pricing_currency = metadata['pricingCurrency']

                item_details = listing_data['item']
                listing.title = item_details['title']
                if 'tags' in item_details:
                    listing.tags = item_details['tags']
                if 'categories' in item_details:
                    listing.categories = item_details['categories']
                if 'price' in item_details:
                    listing.price = item_details['price']
                    try:
                        c = ExchangeRate.objects.get(
                            symbol=listing.pricing_currency)
                        listing.price_value = listing.price / float(
                            c.base_unit) / float(c.rate)
                    except ZeroDivisionError:
                        listing.price_value = 0.0001

                if 'description' in item_details.keys():
                    listing.description = item_details['description']

                if item_details['condition']:
                    listing.condition_type = getattr(Listing,
                                                     item_details['condition'].upper())

                if "images" in item_details.keys():
                    for i, iHashes in enumerate(item_details['images']):
                        iHashes['index'] = i
                        iHashes['listing'] = listing
                        li, li_c = ListingImage.objects.get_or_create(
                            **iHashes)
                        li.save()

                if "moderators" in listing_data:

                    listed_moderators = listing_data['moderators']
                    known_moderators = Profile.objects.filter(
                        pk__in=listed_moderators)
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
                                    from ob.tasks.sync_profile import \
                                        sync_profile
                                    sync_profile(new_mod)

                        moderators = Profile.objects.filter(
                            pk__in=listed_moderators)
                    else:
                        moderators = known_moderators

                    listing.moderators.set(list(moderators))

                if "coupons" in listing_data:
                    for c in listing_data['coupons']:
                        pass

                if "shippingOptions" in listing_data:
                    for so in listing_data['shippingOptions']:
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
