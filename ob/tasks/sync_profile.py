import ipaddress
import json
import logging
import requests
from urllib3.exceptions import SubjectAltNameWarning

from django.conf import settings
from django.dispatch import receiver
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.timezone import now

from ob.models.profile import Profile
from ob.models.profile_address import ProfileAddress
from ob.models.profile_social import ProfileSocial
from ob.models.image import Image
from ob.tasks.sync_ratings import sync_ratings
from ob.tasks.sync_listings import sync_listings
from ob.util import get, moving_average_speed

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
            logger.debug('Good Reponse from: ' + profile.peerID)
            profile_data = json.loads(
                profile_response.content.decode('utf-8'))
            speed_rank = profile_response.elapsed.microseconds
            profile.speed_rank = float(profile.speed_rank) / 2.0 + float(
                speed_rank) / 2.0
            profile.about = profile_data.get('about')
            profile.name = profile_data.get('name')
            profile.location = profile_data.get('location')
            profile.short_description = profile_data.get('shortDescription')
            profile.moderator = profile_data.get('moderator')

            mod_info = profile_data.get('moderatorInfo')
            profile = sync_profile_mod_info(profile,
                                            mod_info) if mod_info else profile

            contact = profile_data.get('contactInfo')
            if contact:
                profile = sync_profile_mod_info_contact(profile, contact)
                add_profile_social_info(profile, contact)

            if mod_info:
                fee = mod_info.get('fee')
                feeType = mod_info.get('feeType')
                if feeType:
                    profile.moderator_fee_type = getattr(Profile, feeType)
                profile.moderator_fee_percentage = fee.get('percentage')
                try:
                    profile.moderator_fee_fixed_currency = fee['fixedFee'][
                        'currencyCode']
                    profile.moderator_fee_fixed_amount = fee['fixedFee'][
                        'amount']
                except KeyError:
                    logger.debug('error geting mod currency')

            profile.nsfw = profile_data.get('nsfw')
            profile.vendor = profile_data.get('vendor')

            profile.pub_date = now()

            profile.avatar = get_image(
                profile_data.get('avatarHashes')
            )

            profile.header = get_image(
                profile_data.get('headerHashes')
            )

            stats = profile_data.get('stats')
            if stats:
                profile.follower_count = stats.get('followerCount')
                # Don't trust the ratings from stats
                # profile.rating_count =
                # profile.rating_average =
            profile.user_agent = get_user_agent(profile.peerID)

            peer_info_url = OB_INFO_URL + profile.peerID
            peer_info_response = get(peer_info_url)
            if peer_info_response.status_code == 200:
                peer_info_data = json.loads(
                    peer_info_response.content.decode('utf-8'))
                if 'Addrs' in peer_info_data.keys():
                    for k in peer_info_data['Addrs']:
                        tmp_ip_type = ''

                        if 'onion' in k:
                            tmp_ip_type = 'PUBLIC'
                            t = ProfileAddress.TOR
                        else:
                            temp_addr = ipaddress.ip_address(
                                k.split('/')[2])
                            if temp_addr.is_global:
                                tmp_ip_type = 'PUBLIC'
                                t = (
                                    ProfileAddress.IPV4 if temp_addr.version == 4 else ProfileAddress.IPV6)
                            else:
                                tmp_ip_type = 'PRIVATE'
                        try:
                            # print(k)
                            if tmp_ip_type == 'PUBLIC':
                                pa = ProfileAddress(address=k, profile=profile,
                                                    address_type=t)
                                pa.save()
                        except IntegrityError:
                            print(
                                "integrity error saving address while scraping")

                    if profile.addresses.filter(
                            address_type=2).exists() and profile.addresses.filter(
                        address_type__in=[0, 1]).exists():
                        profile.connection_type = 1
                    elif not profile.addresses.filter(
                            address_type=2).exists() and profile.addresses.filter(
                        address_type__in=[0, 1]).exists():
                        profile.connection_type = 0
                    elif profile.addresses.filter(
                            address_type=2).exists() and not profile.addresses.filter(
                        address_type__in=[0, 1]).exists():
                        profile.connection_type = 2
            else:
                code = peer_info_response.status_code
                logger.debug("{} fetching {}".format(code, peer_info_url))

            profile.save()
            profile.listing_set.update(active=False)
            if profile.vendor:
                sync_listings(profile)
                sync_ratings(profile)
            else:
                profile.listing_set.update(active=False)
            profile.save()
        else:
            code = profile_response.status_code
            logger.debug('{} fetching {}'.format(code, profile_url))
            speed_rank = settings.CRAWL_TIMEOUT * 1e6

            # 10 try incremental moving average, no model signals
            new_rank = (profile.speed_rank * 0.1) + (speed_rank * 0.9)
            Profile.objects.filter(pk=profile.peerID) \
                .update(speed_rank=new_rank)

    except json.decoder.JSONDecodeError:
        logger.warning("Problem decoding json for peer: " + profile.peerID)

    except requests.exceptions.ReadTimeout:
        moving_average_speed(profile)


def get_image(hash):
    if hash:
        a, a_created = Image.objects.get_or_create(
            **hash)
        return a


def sync_profile_mod_info(profile, mod_info):
    profile.moderator_description = mod_info.get('description')
    profile.moderator_terms = mod_info.get('termsAndConditions')
    profile.moderator_languages = mod_info.get('languages')
    profile.moderator_accepted_currencies = mod_info.get('acceptedCurrencies')
    return profile


def sync_profile_mod_info_contact(profile, contact):
    profile.email = contact.get('email')
    profile.website = contact.get('website')
    profile.phone = contact.get('phoneNumber')
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
    for s in contact.get('social'):
        sa, sa_created = ProfileSocial.objects.get_or_create(
            social_type=s['type'],
            username=s['username'],
            proof=s['proof'],
            profile=profile
        )
        sa.save()


def get_profile_address(profile, address):
    if 'onion' in address:
        tmp_ip_type = 'PUBLIC'
        t = ProfileAddress.TOR
    else:
        temp_addr = ipaddress.ip_address(
            address.split('/')[2])
        if temp_addr.is_global:
            tmp_ip_type = 'PUBLIC'
            t = ProfileAddress.IPV4 if temp_addr.version == 4 \
                else ProfileAddress.IPV6
        else:
            tmp_ip_type = 'PRIVATE'
    try:
        if tmp_ip_type == 'PUBLIC':
            t = ProfileAddress.IPV4 if temp_addr.version == 4 \
                else ProfileAddress.IPV6

            pa = ProfileAddress(address=address, profile=profile,
                                address_type=t)
            pa.save()
    except IntegrityError:
        logger.debug(
            "integrity error saving address while scraping")


def get_profile_connection_type(profile):
    c = None
    if profile.addresses.filter(address_type=2).exists() and \
            profile.addresses.filter(address_type__in=[0, 1]).exists():
        c = 1
    elif not profile.addresses \
            .filter(address_type=2).exists() and profile.addresses \
            .filter(address_type__in=[0, 1]).exists():
        c = 0
    elif profile.addresses.filter(
            address_type=2).exists() and not profile.addresses \
            .filter(address_type__in=[0, 1]).exists():
        c = 2
    return c
