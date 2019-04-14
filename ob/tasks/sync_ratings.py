import json
import logging
from lxml import etree as lxmletree
import requests

from django.conf import settings
from django.db.utils import IntegrityError
from django.utils.dateparse import parse_datetime

from ob.models import Listing, ListingRating
from ob.util import get

logger = logging.getLogger(__name__)

IPNS_HOST = settings.IPNS_MAINNET_HOST


def sync_ratings(profile):
    parser = lxmletree.HTMLParser()
    url = IPNS_HOST + profile.peerID + '/ratings/'

    r = get(url)
    tree = lxmletree.fromstring(r.content, parser)

    rating_files = tree.xpath('//table/tr/td[contains(.,"Qm")]/a/text()')

    ratings_urls = [url + f for f in rating_files]
    for rating_url in ratings_urls:
        try:
            response = get(rating_url)
            if response.status_code == 200:
                logger.debug('BEGIN rating sync ' + profile.peerID)
                try:
                    rating_data = json.loads(
                        response.content.decode('utf-8'))
                    listing_slug = \
                        rating_data['ratingData']['vendorSig']['metadata'][
                            'listingSlug']
                    try:
                        listing = Listing.objects.get(profile=profile,
                                                      slug=listing_slug)
                        r_pk = rating_data['ratingData']['ratingKey']
                        try:
                            lr, lr_c = ListingRating.objects.get_or_create(
                                profile=profile,
                                listing=listing,
                                pk=r_pk)
                            rating = rating_data['ratingData']
                            lr.overall = rating.get("overall")
                            lr.quality = rating.get("quality")
                            lr.description = rating.get("description")
                            lr.delivery_speed = rating.get("deliverySpeed")
                            lr.customer_service = rating.get("customerService")
                            lr.timestamp = parse_datetime(
                                rating.get("timestamp"))
                            lr.review = rating.get("review")
                            lr.save()
                        except IntegrityError as err:
                            logger.debug("DB Integrity Error: {0}".format(err))
                            # listing.save()
                    except TypeError:
                        logger.debug("bad json in listing " + profile.peerID)
                    except Listing.MultipleObjectsReturned:
                        logger.debug(
                            "Ignoring multiple items with same slug " + profile.peerID)
                    except Listing.DoesNotExist:
                        logger.debug(
                            "Ignoring rating for listing we couldn't find: " + profile.peerID)
                except json.decoder.JSONDecodeError:
                    logger.debug(
                        "Problem decoding json for listings of peer: " + profile.peerID)
        except requests.exceptions.ReadTimeout:
            logger.debug("listing peerID " + profile.peerID + " timeout")

    for l in profile.listing_set.all():
        l.save()
