import json
import requests
from django.conf import settings
from django.db.utils import IntegrityError
from django.utils import timezone

from django.dispatch import receiver

from urllib3.exceptions import SubjectAltNameWarning

import ipaddress
import os


# Profile
def sync(p):
    OB_INFO_URL = OB_HOST + 'peerinfo/'
    profile_url = OB_HOST + 'profile/' + p.peerID
    try:
        profile_response = requests_get_wrap(profile_url)
        if profile_response.status_code == 200:
            print('Good Reponse from: ' + p.peerID)
            profile_data = json.loads(profile_response.content.decode('utf-8'))
            speed_rank = profile_response.elapsed.microseconds
            p.speed_rank = float(p.speed_rank) / 2.0 + float(speed_rank) / 2.0
            p.about = profile_data['about']
            p.name = profile_data['name']
            p.location = profile_data['location']
            p.short_description = profile_data['shortDescription']
            p.moderator = profile_data['moderator']
            if 'moderatorInfo' in profile_data.keys():
                mod_info = profile_data['moderatorInfo']
                p.moderator_description = (mod_info['description'] if 'description' in mod_info.keys() else '')
                p.moderator_terms = (
                    mod_info['termsAndConditions'] if 'termsAndConditions' in mod_info.keys() else '')
                p.moderator_languages = (mod_info['languages'] if 'languages' in mod_info.keys() else '')
                # This is not a property with sqlite3
                # p.moderator_languages_array = (mod_info['languages'] if 'languages' in mod_info.keys() else [])
                p.moderator_accepted_currencies = (
                    mod_info['acceptedCurrencies'] if 'acceptedCurrencies' in mod_info.keys() else '')
                # Array properties don't work with sqlite3, use the text field.
                # p.moderator_accepted_currencies_array = (mod_info['acceptedCurrencies'] if 'acceptedCurrencies' in mod_info.keys() else [])
                if 'fee' in mod_info.keys():
                    fee = mod_info['fee']
                    feeType = (mod_info['feeType'] if 'feeType' in mod_info.keys() else '')
                    if feeType == 'PERCENTAGE':
                        p.moderator_fee_type = 1
                    elif feeType == 'FIXED':
                        p.moderator_fee_type = 2
                    elif feeType == 'FIXED_PLUS_PERCENTAGE':
                        p.moderator_fee_type = 3
                    else:
                        p.moderator_fee_type = 0
                    p.moderator_fee_percentage = (fee['percentage'] if 'percentage' in fee.keys() else '')
                    try:
                        p.moderator_fee_fixed_currency = fee['fixedFee']['currencyCode']
                        p.moderator_fee_fixed_amount = fee['fixedFee']['amount']
                    except KeyError:
                        print('error geting mod currency')

            if 'contactInfo' in profile_data.keys():
                # print('found contact info')

                contact = profile_data['contactInfo']
                # print(contact)
                p.email = (contact['email'] if 'email' in contact.keys() else '')
                p.website = (contact['website'] if 'website' in contact.keys() else '')
                p.phone = (contact['phoneNumber'] if 'phoneNumber' in contact.keys() else '')

                if 'social' in contact.keys():
                    for s in contact['social']:
                        try:
                            sa, sa_created = ProfileSocial.objects.get_or_create(social_type=s['type'],
                                                                                 username=s['username'],
                                                                                 proof=s['proof'],
                                                                                 profile=self
                                                                                 )
                            sa.save()
                        except:
                            pass

            if 'nsfw' in profile_data.keys():
                p.nsfw = profile_data['nsfw']
            p.vendor = profile_data['vendor']

            p.pub_date = timezone.now()

            if "avatarHashes" in profile_data.keys():
                a, aCreated = Image.objects.get_or_create(**profile_data['avatarHashes'])
                p.avatar = a
            if "headerHashes" in profile_data.keys():
                h, hCreated = Image.objects.get_or_create(**profile_data['headerHashes'])
                p.header = h

            if "stats" in profile_data.keys():
                # print("found Stats")
                stats = profile_data['stats']
                p.follower_count = (stats['followerCount'] if 'followerCount' in stats.keys() else 0)
                # p.rating_count = ( stats['ratingCount'] if 'ratingCount' in stats.keys() else '')
                # p.rating_average = ( stats['averageRating'] if 'averageRating' in stats.keys() else '')

            user_agent_url = IPNS_HOST + p.peerID + '/user_agent'
            user_agent_response = requests_get_wrap(user_agent_url)
            if user_agent_response.status_code == 200:
                p.user_agent = user_agent_response.content.decode('utf-8')
            else:
                p.user_agent = 'Error : ' + user_agent_response.status_code

            peer_info_url = OB_INFO_URL + p.peerID
            peer_info_response = requests_get_wrap(peer_info_url)
            if peer_info_response.status_code == 200:
                peer_info_data = json.loads(peer_info_response.content.decode('utf-8'))
                if 'Addrs' in peer_info_data.keys():
                    for k in peer_info_data['Addrs']:
                        tmp_ip_type = ''

                        if 'onion' in k:
                            tmp_ip_type = 'PUBLIC'
                            t = ProfileAddress.TOR
                        else:
                            temp_addr = ipaddress.ip_address(k.split('/')[2])
                            if temp_addr.is_global:
                                tmp_ip_type = 'PUBLIC'
                                t = (ProfileAddress.IPV4 if temp_addr.version == 4 else ProfileAddress.IPV6)
                            else:
                                tmp_ip_type = 'PRIVATE'
                        try:
                            # print(k)
                            if tmp_ip_type == 'PUBLIC':
                                pa = ProfileAddress(address=k, profile=self, address_type=t)
                                pa.save()
                        except IntegrityError:
                            print("integrity error saving address while scraping")

                    if p.addresses.filter(address_type=2).exists() and p.addresses.filter(
                            address_type__in=[0, 1]).exists():
                        p.connection_type = 1
                    elif not p.addresses.filter(address_type=2).exists() and p.addresses.filter(
                            address_type__in=[0, 1]).exists():
                        p.connection_type = 0
                    elif p.addresses.filter(address_type=2).exists() and not p.addresses.filter(
                            address_type__in=[0, 1]).exists():
                        p.connection_type = 2
            else:
                print('Error ' + str(peer_info_response.status_code) + '  fetching ' + peer_info_url)

            p.save()
            p.listing_set.update(active=False)
            if p.vendor:
                p.update_listings(testnet)
                p.update_ratings(testnet)
            else:
                p.listing_set.update(active=False)
            p.save()
        else:
            print('Error ' + str(profile_response.status_code) + '  fetching ' + profile_url)
            speed_rank = settings.CRAWL_TIMEOUT * 1e6

            # moving average
            new_rank = (p.speed_rank * 0.1) + (speed_rank * 0.9)
            Profile.objects.filter(pk=p.peerID).update(speed_rank=new_rank)

    except json.decoder.JSONDecodeError:
        print("Problem decoding json for peer: " + p.peerID)

    except requests.exceptions.ReadTimeout:
        speed_rank = settings.CRAWL_TIMEOUT * 1e6
        new_rank = p.speed_rank / 2.0 + speed_rank / 2.0
        Profile.objects.filter(pk=p.peerID).update(speed_rank=new_rank, attempt=timezone.now())
        print("peerID " + p.peerID + " timeout")
