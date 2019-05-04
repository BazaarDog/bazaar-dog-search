import json
import logging
from lxml import etree as lxmletree
from requests.exceptions import ConnectionError, ReadTimeout

from django.conf import settings
from django.db.utils import IntegrityError
from django.utils.dateparse import parse_datetime

from ob.models.listing import Listing
from ob.models.listing_rating import ListingRating
from ob.models.util import get

logger = logging.getLogger(__name__)

IPNS_HOST = settings.IPNS_MAINNET_HOST


def sync_ratings(profile):
    parser = lxmletree.HTMLParser()
    url = IPNS_HOST + profile.peerID + '/ratings/'
    try:
        r = get(url)
        tree = lxmletree.fromstring(r.content, parser)

        rating_files = tree.xpath('//table/tr/td[contains(.,"Qm")]/a/text()')

        ratings_urls = [url + f for f in rating_files]
        for rating_url in ratings_urls:
            try:
                sync_one_rating(rating_url, profile)
            except (ConnectionError, ReadTimeout):
                logger.debug("listing peerID " + profile.peerID + " timeout")

        for l in profile.listing_set.all():
            l.save()
    except (ConnectionError, ReadTimeout):
        logger.info("read timeout on ratings")


def sync_one_rating(rating_url, profile):
    response = get(rating_url)
    if response.status_code == 200:
        logger.debug('BEGIN rating sync ' + profile.peerID)
        try:
            rating_data = json.loads(response.content.decode('utf-8'))
            listing_slug, r_pk = get_listing_slug(rating_data)
            try:
                listing = Listing.objects.get(profile=profile,
                                              slug=listing_slug)
                try:
                    update_rating(profile, listing, r_pk, rating_data)
                except IntegrityError as err:
                    logger.debug("DB Integrity Error: {0}".format(err))
                    # listing.save()
            except Listing.DoesNotExist:
                logger.debug("Ignoring rating for listing we don't have:"
                             "{peer}"
                             "{slug}".format(peer=profile.peerID,
                                             slug=listing_slug))
        except TypeError:
            logger.debug("ignoring rating")
        except json.decoder.JSONDecodeError:
            logger.debug(
                "Problem decoding json for listings of peer: " + profile.peerID)


def update_rating(profile, listing, r_pk, rating_data):
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


def get_listing_slug(data):

    try:
        r_pk = data['ratingData']['ratingKey']
    except KeyError:
        logger.info("couldn't get rating key")

    try:
        slug = data['ratingData']['vendorSig']['metadata']['listingSlug']
    except KeyError:
        logger.info("couldn't find listing slug")

    if slug and r_pk:
        return slug, r_pk

