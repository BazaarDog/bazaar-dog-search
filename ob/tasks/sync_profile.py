import ipaddress
import json
import logging
import requests

from django.conf import settings
from django.db.utils import IntegrityError
from django.utils.timezone import now

from ob.models.profile import Profile
from ob.models.profile_address import ProfileAddress
from ob.models.profile_social import ProfileSocial
from ob.models.image import Image
from ob.tasks.sync_ratings import sync_ratings
from ob.tasks.sync_listings import sync_listings
from ob.models.util import get

logger = logging.getLogger(__name__)

OB_HOST = settings.OB_MAINNET_HOST
IPNS_HOST = settings.IPNS_MAINNET_HOST
OB_INFO_URL = OB_HOST + 'peerinfo/'


# Sync a Profile
def sync_profile(profile):
    profile_url = OB_HOST + 'profile/' + profile.peerID
    try:
        profile_response = get(profile_url)
        if profile_response.status_code == 200:
            profile_data = json.loads(
                profile_response.content.decode('utf-8')
            )
            new_speed_rank = profile_response.elapsed.microseconds
            profile.moving_average_speed(new_speed_rank)
            sync_profile_data(profile, profile_data)
        else:
            code = profile_response.status_code
            logger.debug('{} fetching {}'.format(code, profile_url))
            profile.moving_average_speed(settings.CRAWL_TIMEOUT * 1e6)

    except json.decoder.JSONDecodeError:
        logger.warning("Problem decoding json for peer: " + profile.peerID)

    except requests.exceptions.ReadTimeout:
        profile.moving_average_speed(settings.CRAWL_TIMEOUT * 1e6)


def sync_profile_data(profile, profile_data):
    profile.about = profile_data.get('about')
    profile.name = profile_data.get('name')
    profile.location = profile_data.get('location')
    profile.short_description = profile_data.get('shortDescription')
    profile.moderator = profile_data.get('moderator')
    profile.nsfw = profile_data.get('nsfw')
    profile.vendor = profile_data.get('vendor')
    profile.pub_date = now()
    profile = sync_profile_mod_info(
        profile,
        profile_data.get('moderatorInfo')
    )

    profile = sync_profile_contact_info(
        profile,
        profile_data.get('contactInfo')
    )

    profile.avatar = get_image(
        profile_data.get('avatarHashes')
    )
    profile.header = get_image(
        profile_data.get('headerHashes')
    )

    profile.follower_count = get_profile_follower_count(profile_data)
    profile.user_agent = get_user_agent(profile.peerID)
    profile.connection_type = get_profile_connection_type(profile)

    profile.save()
    if profile.vendor:
        sync_listings(profile)
        sync_ratings(profile)
    else:
        profile.listing_set.update(active=False)


def get_image(hash):
    if hash:
        a, a_created = Image.objects.get_or_create(
            **hash)
        return a


def sync_profile_mod_info(profile, mod_info):
    if mod_info:
        profile.moderator_description = mod_info.get('description')
        profile.moderator_terms = mod_info.get('termsAndConditions')
        profile.moderator_languages = mod_info.get('languages')
        profile.moderator_accepted_currencies = mod_info.get(
            'acceptedCurrencies'
        )
        fee = mod_info.get('fee')
        fee_type = mod_info.get('feeType')
        if fee_type:
            profile.moderator_fee_type = getattr(Profile, fee_type)
        profile.moderator_fee_percentage = fee.get('percentage')
        fixed = fee.get('fixedFee')
        if fixed:
            profile.moderator_fee_fixed_currency = fixed.get('currencyCode')
            profile.moderator_fee_fixed_amount = fixed.get('amount')
    return profile


def sync_profile_contact_info(profile, contact):
    if contact:
        profile.email = contact.get('email')
        profile.website = contact.get('website')
        profile.phone = contact.get('phoneNumber')
        add_profile_social_info(profile, contact)
    return profile


def get_user_agent(peer_id):
    user_agent_url = IPNS_HOST + peer_id + '/user_agent'
    user_agent_response = get(user_agent_url)
    if user_agent_response.status_code == 200:
        ua = user_agent_response.content.decode('utf-8')
    else:
        ua = 'Error : {}'.format(user_agent_response.status_code)
    return ua


def add_profile_social_info(profile, contact):
    for s in contact.get('social') or []:
        sa, sa_created = ProfileSocial.objects.get_or_create(
            social_type=s['type'],
            username=s['username'],
            proof=s['proof'],
            profile=profile
        )
        sa.save()

def get_profile_connection_type(profile):
    if profile.has_tor():
        if profile.has_clearnet():
            return Profile.DUAL
        else:
            return Profile.TOR
    elif profile.has_clearnet():
        return Profile.CLEAR


def get_profile_follower_count(profile_data):
    if profile_data.get('stats'):
        return profile_data.get('stats').get('followerCount')


def get_profile_connection(profile):
    peer_info_url = OB_INFO_URL + profile.peerID
    peer_info_response = get(peer_info_url)
    if peer_info_response.status_code == 200:
        add_data = json.loads(peer_info_response.content.decode('utf-8'))
        get_profile_address_type(add_data, profile)

    else:
        code = peer_info_response.status_code
        logger.debug("{} fetching {}".format(code, peer_info_url))


def get_profile_address_type(add_data, profile):
    for k in add_data.get('Addrs') or []:
        if 'onion' in k:
            t = ProfileAddress.TOR
        else:
            temp_addr = ipaddress.ip_address(k.split('/')[2])
            if temp_addr.is_global:
                t = temp_addr.version == 4
        if t in ProfileAddress.ADDRESS_TYPE_DICT:
            pa = ProfileAddress(address=k, profile=profile,
                                address_type=t)
            pa.save()
