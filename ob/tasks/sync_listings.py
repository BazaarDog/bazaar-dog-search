import json
import logging
import requests
from django.conf import settings

from ob.models import Listing, ExchangeRate


logger = logging.getLogger(__name__)
OB_HOST = settings.OB_MAINNET_HOST


def sync_listings(profile):

    listing_url = OB_HOST + 'listings/' + profile.peerID

    try:
        from ob.util import get
        from ob.tasks.sync_listing import sync_listing
        response = get(listing_url)
        if response.status_code == 200:
            # logger.info('BEGIN listing sync' + profile.peerID)
            try:
                for listing_data in json.loads(
                        response.content.decode('utf-8')):
                    # logger.info(profile.peerID + ': ' + listing_data['slug'])
                    listing, listing_created = Listing.objects.get_or_create(
                        profile=profile,
                        slug=listing_data['slug'])

                    if listing_created:
                        listing.hash = listing_data['hash']
                        listing.title = listing_data['title']
                        listing.description = listing_data['description']
                        if listing.listingreport_set.count() == 0:
                            listing.nsfw = listing_data['nsfw']
                        # Don't take ratings here

                        listing.price = listing_data['price']['amount']
                        listing.pricing_currency = listing_data['price'][
                            'currencyCode']
                        c, fx_created = ExchangeRate.objects.get_or_create(
                            symbol=listing.pricing_currency)
                        try:
                            listing.price_value = listing.price / float(
                                c.base_unit) / float(c.rate)
                        except ZeroDivisionError:
                            listing.price_value = 0.0001
                        listing.network = ('mainnet')

                        if "SERVICE" in listing_data['contractType']:
                            listing.contract_type = Listing.SERVICE
                        elif "DIGITAL_GOOD" in listing_data['contractType']:
                            listing.contract_type = Listing.DIGITAL_GOOD
                        elif "PHYSICAL_GOOD" in listing_data[
                            'contractType']:
                            listing.contract_type = Listing.PHYSICAL_GOOD
                        elif "CROWD_FUND" in listing_data['contractType']:
                            listing.contract_type = Listing.CROWD_FUND
                        elif "CRYPTOCURRENCY" in listing_data[
                            'contractType']:
                            listing.contract_type = Listing.CRYPTOCURRENCY
                        if 'averageRating' in listing_data.keys():
                            listing.rating_average_stale = listing_data[
                                'averageRating']
                        if 'ratingCount' in listing_data.keys():
                            listing.rating_count_stale = listing_data[
                                'ratingCount']
                        if 'freeShipping' in listing_data.keys():
                            listing.free_shipping = listing_data[
                                'freeShipping']
                        listing.active = True
                    else:
                        if 'averageRating' in listing_data.keys():
                            listing.rating_average_stale = listing_data[
                                'averageRating']
                        if 'ratingCount' in listing_data.keys():
                            listing.rating_count_stale = listing_data[
                                'ratingCount']
                        if 'freeShipping' in listing_data.keys():
                            listing.free_shipping = listing_data[
                                'freeShipping']
                        listing.active = True
                    sync_listing(listing)

            except json.decoder.JSONDecodeError:
                logger.info(
                    "Problem decoding json for listings of peer: " + profile.peerID)
            except TypeError:
                profile.listing_set.update(active=False)
                logger.info("No listings " + profile.peerID)

            except KeyError:
                logger.info(
                    "Problem parsing json for listings of peer: " + profile.peerID)

    except requests.exceptions.ReadTimeout:
        logger.info("listing peerID " + profile.peerID + " timeout")