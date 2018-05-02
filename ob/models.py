import math
import json
from pathlib import Path
import requests
from random import randint

from datetime import timedelta
from django.conf import settings
from django.db import models
from django.db.models import Count, Sum, Avg, F
from django.db.models.signals import post_save
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
#from django.contrib.postgres.fields import ArrayField

from django.dispatch import receiver

from urllib3.exceptions import SubjectAltNameWarning

import ipaddress
import os
import asyncio
requests.packages.urllib3.disable_warnings(SubjectAltNameWarning)

try:
    from obscure import get_listing_rank, get_profile_rank
except ImportError:
    from custom import get_listing_rank, get_profile_rank


def requests_get_wrap(url, timeout=settings.CRAWL_TIMEOUT):
    print(url)
    if 'https' in url:

        if Path(settings.OB_CERTIFICATE).is_file():
            return requests.get(url,
                                timeout=timeout,
                                auth=settings.OB_API_AUTH,
                                verify=settings.OB_CERTIFICATE)
        else:
            print("couldn't find ssl cert for a secure connection to openbazaar-go server... ")
            raise Exception
    else:
        return requests.get(url,
                            timeout=settings.CRAWL_TIMEOUT)

def requests_post_wrap(url,data):
    print(url)
    if 'https' in url:
        if Path(settings.OB_CERTIFICATE).is_file():
            return requests.post(url,
                                 data=data,
                                 timeout=settings.CRAWL_TIMEOUT,
                                 auth=settings.OB_API_AUTH,
                                 verify=settings.OB_CERTIFICATE
                                 )
        else:
            raise Exception
    else:
        return requests.post(url,
                             data=data,
                             timeout=settings.CRAWL_TIMEOUT)


class ExchangeRate(models.Model):
    symbol = models.TextField(null=True)
    rate = models.FloatField(default=0)
    base_unit = models.IntegerField(default=100)


class ListingImage(models.Model):
    listing = models.ForeignKey('Listing', related_name='images', on_delete=models.CASCADE)
    index = models.PositiveIntegerField(verbose_name='Index')
    filename = models.TextField(null=True)
    original = models.TextField(null=True)
    large = models.TextField(null=True)
    medium = models.TextField(null=True)
    small = models.TextField(null=True)
    tiny = models.TextField(null=True)


class ProfileAddress(models.Model):
    IPV4 = 0
    IPV6 = 1
    TOR = 2

    ADDRESS_TYPE_CHOICES = (
        (IPV4, 'ipv4'),
        (IPV6, 'ipv6'),
        (TOR, 'onion'),
    )
    ADDRESS_TYPE_DICT = dict(ADDRESS_TYPE_CHOICES)

    profile = models.ForeignKey('Profile', related_name='addresses', on_delete=models.CASCADE)
    address = models.TextField(blank=True, default='')
    address_type = models.IntegerField(choices=ADDRESS_TYPE_CHOICES, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)


class ProfileSocial(models.Model):
    profile = models.ForeignKey('Profile', related_name='social', on_delete=models.CASCADE)
    social_type = models.TextField(blank=True, default='')
    username = models.TextField(blank=True, default='')
    proof = models.TextField(blank=True, default='')


class Image(models.Model):
    filename = models.TextField(null=True)
    original = models.TextField(null=True)
    large = models.TextField(null=True)
    medium = models.TextField(null=True)
    small = models.TextField(null=True)
    tiny = models.TextField(null=True)


class Profile(models.Model):
    ANY = 0
    PERCENTAGE = 1
    FIXED = 2
    FIXED_PLUS_PERCENTAGE = 3

    MODERATOR_FEE_TYPE_CHOICES = (
        (ANY, _('Any')),
        (PERCENTAGE, _('Percentage')),
        (FIXED, _('Fixed')),
        (FIXED_PLUS_PERCENTAGE, _('Fixed Plus Percentage')),
    )
    MODERATOR_FEE_TYPE_DICT = dict(MODERATOR_FEE_TYPE_CHOICES)

    ANY = ''
    CLEAR = 0
    DUAL = 1
    TOR = 2
    OFFLINE = 3

    CONNECTION_TYPE_CHOICES = (
        (ANY, _('Any')),
        (CLEAR, _('Clearnet')),
        (DUAL, _('Dual Stack')),
        (TOR, _('Tor Only')),
        (OFFLINE, _('IPFS Cached')),
    )
    CONNECTION_TYPE_DICT = dict(CONNECTION_TYPE_CHOICES)

    peerID = models.CharField(primary_key=True, max_length=46)
    serialized_record = models.TextField(blank=True, default='')
    name = models.TextField(blank=True, default='')
    about = models.TextField(blank=True, default='')
    handle = models.TextField(blank=True, default='')
    header = models.ForeignKey(Image, related_name='profile_header', null=True, on_delete=models.CASCADE)
    avatar = models.ForeignKey(Image, related_name='profile_avatar', null=True, on_delete=models.CASCADE)
    network = models.TextField(default='mainnet', null=False, blank=False)
    user_agent = models.TextField(blank=True, default='')
    location = models.TextField(blank=True, default='')
    short_description = models.TextField(blank=True, default='')
    moderator = models.BooleanField(default=False)
    moderator_description = models.TextField(default='')
    moderator_terms = models.TextField(default='')

    moderator_languages = models.TextField(default='')
    # Array fields will not work with sqlite3, use the text field instead
    # moderator_languages_array = ArrayField(models.CharField(max_length=10), null=True, blank=True)

    moderator_accepted_currencies = models.TextField(default='')
    # Array fields will not work with sqlite3, use the text field instead
    # moderator_accepted_currencies_array = ArrayField(models.CharField(max_length=10), null=True, blank=True)

    moderator_fee_type = models.IntegerField(choices=MODERATOR_FEE_TYPE_CHOICES, default=0)
    moderator_fee_percentage = models.FloatField(default=0, null=False, blank=False)
    moderator_fee_fixed_currency = models.TextField(default='')
    moderator_fee_fixed_amount = models.FloatField(default=0, null=False, blank=False)

    website = models.TextField(default='')
    email = models.TextField(default='')
    phone = models.TextField(default='')

    online = models.BooleanField(default=False)

    nsfw = models.BooleanField(default=False)
    vendor = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    scam = models.BooleanField(default=False)
    illegal_in_us = models.BooleanField(default=False)
    dog_follows = models.BooleanField(default=False)

    follower_count = models.IntegerField(default=0, null=False, blank=False)
    rank = models.IntegerField(default=0, null=False, blank=False)
    speed_rank = models.FloatField(default=1e7, null=False, blank=False)

    listing_count = models.IntegerField(default=0, null=False, blank=False)
    moderated_items_count = models.IntegerField(default=0, null=False, blank=False)

    rating_count = models.IntegerField(default=0, null=False, blank=False)
    rating_average = models.FloatField(default=0, null=False, blank=False)
    rating_dot = models.FloatField(default=0, null=False, blank=False)

    connection_type = models.IntegerField(choices=CONNECTION_TYPE_CHOICES, default=OFFLINE)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    attempt = models.DateTimeField(auto_now=True)
    was_online = models.DateTimeField(auto_now=False,null=True)
    pinged = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rank']

    def get_seralized_record(self, testnet=False):

        try:
            OB_HOST = settings.OB_MAINNET_HOST if not testnet else settings.OB_TESTNET_HOST
            profile_url = OB_HOST + 'ipns/' + self.peerID
            peer_response = requests_get_wrap(profile_url)
            if peer_response.status_code == 200:
                peer_data = json.loads(peer_response.content.decode('utf-8'))
                return peer_data['serializedRecord']
            else:
                print('{}'.format(peer_response.status_code))
        except IndexError:
            print('index error getting serialized record')

    # profile

    def should_update(self):

        if self.online or True:
            if self.serialized_record is not self.get_seralized_record():
                if self.attempt < now() - timedelta(hours=settings.SHORTEST_UPDATE_HOURS):
                    return True
                else:
                    print("too soon")
                    return False
            else:
                Profile.objects.filter(pk=self.peerID).update(modified=now())
                print("no change")
                return False
        else:
            print("offline")
            return False





    # '4002/ob/peerinfo/QmTQNzpvq1Lgx6NvXhnoiWirLV1oQbF9LJZwMENKoPYVon'

    def get_neighbors(self, testnet=False):
        try:
            OB_HOST = settings.OB_MAINNET_HOST if not testnet else settings.OB_TESTNET_HOST
            closestpeers_url = OB_HOST + 'closestpeers/' + self.peerID
            peer_response = requests_get_wrap(closestpeers_url)
            if peer_response.status_code == 200:
                peer_data = json.loads(peer_response.content.decode('utf-8'))
                return peer_data

        except IndexError:
            print('index error getting address')

    # Profile
    def sync(self, testnet=False):
        import requests
        import json
        IPNS_HOST = settings.IPNS_TESTNET_HOST  if self.network == 'testnet' else settings.IPNS_MAINNET_HOST
        OB_HOST = settings.OB_TESTNET_HOST if self.network == 'testnet' else settings.OB_MAINNET_HOST
        OB_INFO_URL = OB_HOST + 'peerinfo/'

        profile_url = IPNS_HOST + self.peerID + '/profile.json'
        try:
            profile_response = requests_get_wrap(profile_url)
            if profile_response.status_code == 200:
                print('Good Reponse from: ' + self.peerID)
                profile_data = json.loads(profile_response.content.decode('utf-8'))
                speed_rank = profile_response.elapsed.microseconds
                self.speed_rank = float(self.speed_rank) / 2.0 + float(speed_rank) / 2.0
                self.about = profile_data['about']
                self.name = profile_data['name']
                self.location = profile_data['location']
                self.short_description = profile_data['shortDescription']
                self.moderator = profile_data['moderator']
                if 'moderatorInfo' in profile_data.keys():
                    mod_info = profile_data['moderatorInfo']
                    self.moderator_description = (mod_info['description'] if 'description' in mod_info.keys() else '')
                    self.moderator_terms = (
                        mod_info['termsAndConditions'] if 'termsAndConditions' in mod_info.keys() else '')
                    self.moderator_languages = (mod_info['languages'] if 'languages' in mod_info.keys() else '')
                    # This is not a property with sqlite3
                    # self.moderator_languages_array = (mod_info['languages'] if 'languages' in mod_info.keys() else [])
                    self.moderator_accepted_currencies = (
                        mod_info['acceptedCurrencies'] if 'acceptedCurrencies' in mod_info.keys() else '')
                    # Array properties don't work with sqlite3, use the text field.
                    # self.moderator_accepted_currencies_array = (mod_info['acceptedCurrencies'] if 'acceptedCurrencies' in mod_info.keys() else [])
                    if 'fee' in mod_info.keys():
                        fee = mod_info['fee']
                        feeType = (mod_info['feeType'] if 'feeType' in mod_info.keys() else '')
                        if feeType == 'PERCENTAGE':
                            self.moderator_fee_type = 1
                        elif feeType == 'FIXED':
                            self.moderator_fee_type = 2
                        elif feeType == 'FIXED_PLUS_PERCENTAGE':
                            self.moderator_fee_type = 3
                        else:
                            self.moderator_fee_type = 0
                        self.moderator_fee_percentage = (fee['percentage'] if 'percentage' in fee.keys() else '')
                        try:
                            self.moderator_fee_fixed_currency = fee['fixedFee']['currencyCode']
                            self.moderator_fee_fixed_amount = fee['fixedFee']['amount']
                        except KeyError:
                            print('error geting mod currency')

                if 'contactInfo' in profile_data.keys():
                    # print('found contact info')

                    contact = profile_data['contactInfo']
                    # print(contact)
                    self.email = (contact['email'] if 'email' in contact.keys() else '')
                    self.website = (contact['website'] if 'website' in contact.keys() else '')
                    self.phone = (contact['phoneNumber'] if 'phoneNumber' in contact.keys() else '')

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
                    self.nsfw = profile_data['nsfw']
                self.vendor = profile_data['vendor']

                self.pub_date = timezone.now()

                if "avatarHashes" in profile_data.keys():
                    a, aCreated = Image.objects.get_or_create(**profile_data['avatarHashes'])
                    self.avatar = a
                if "headerHashes" in profile_data.keys():
                    h, hCreated = Image.objects.get_or_create(**profile_data['headerHashes'])
                    self.header = h

                if "stats" in profile_data.keys():
                    # print("found Stats")
                    stats = profile_data['stats']
                    self.follower_count = (stats['followerCount'] if 'followerCount' in stats.keys() else 0)
                    # self.rating_count = ( stats['ratingCount'] if 'ratingCount' in stats.keys() else '')
                    # self.rating_average = ( stats['averageRating'] if 'averageRating' in stats.keys() else '')

                user_agent_url = IPNS_HOST + self.peerID + '/user_agent'
                user_agent_response = requests_get_wrap(user_agent_url)
                if user_agent_response.status_code == 200:
                    self.user_agent = user_agent_response.content.decode('utf-8')
                else:
                    self.user_agent = 'Error : ' + user_agent_response.status_code

                peer_info_url = OB_INFO_URL + self.peerID
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

                        if self.addresses.filter(address_type=2).exists() and self.addresses.filter(
                                address_type__in=[0, 1]).exists():
                            self.connection_type = 1
                        elif not self.addresses.filter(address_type=2).exists() and self.addresses.filter(
                                address_type__in=[0, 1]).exists():
                            self.connection_type = 0
                        elif self.addresses.filter(address_type=2).exists() and not self.addresses.filter(
                                address_type__in=[0, 1]).exists():
                            self.connection_type = 2
                else:
                    print('Error ' + str(peer_info_response.status_code) + '  fetching ' + peer_info_url)

                self.save()
                self.listing_set.update(active=False)
                if self.vendor:
                    self.update_listings(testnet)
                    self.update_ratings(testnet)
                else:
                    self.listing_set.update(active=False)
                self.save()
            else:
                print('Error ' + str(profile_response.status_code) + '  fetching ' + profile_url)
                speed_rank = settings.CRAWL_TIMEOUT * 1e6

                # moving average
                new_rank = (self.speed_rank * 0.1) + (speed_rank * 0.9)
                Profile.objects.filter(pk=self.peerID).update(speed_rank=new_rank)

        except json.decoder.JSONDecodeError:
            print("Problem decoding json for peer: " + self.peerID)

        except requests.exceptions.ReadTimeout:
            speed_rank = settings.CRAWL_TIMEOUT * 1e6
            new_rank = self.speed_rank / 2.0 + speed_rank / 2.0
            Profile.objects.filter(pk=self.peerID).update(speed_rank=new_rank, attempt=timezone.now())
            print("peerID " + self.peerID + " timeout")

    def update_ratings(self, testnet=False):
        import requests
        from lxml import etree as lxmletree
        import json
        IPNS_HOST = settings.IPNS_MAINNET_HOST if not testnet else settings.IPNS_TESTNET_HOST
        OB_HOST = settings.OB_MAINNET_HOST if not testnet else settings.OB_TESTNET_HOST

        parser = lxmletree.HTMLParser()
        url = IPNS_HOST + self.peerID + '/ratings/'

        r = requests_get_wrap(url)
        tree = lxmletree.fromstring(r.content, parser)

        rating_files = tree.xpath('//table/tr/td[contains(.,"Qm")]/a/text()')

        ratings_urls = [url + f for f in rating_files]
        for rating_url in ratings_urls:
            try:
                response = requests_get_wrap(rating_url)
                if response.status_code == 200:
                    print('BEGIN rating sync ' + self.peerID)
                    try:
                        rating_data = json.loads(response.content.decode('utf-8'))
                        listing_slug = rating_data['ratingData']['vendorSig']['metadata']['listingSlug']
                        try:
                            listing = Listing.objects.get(profile=self, slug=listing_slug)
                            r_pk = rating_data['ratingData']['ratingKey']
                            try:
                                lr, lr_c = ListingRating.objects.get_or_create(profile=self,
                                                                               listing=listing,
                                                                               pk=r_pk)
                                lr.overall = rating_data['ratingData']["overall"]
                                lr.quality = rating_data['ratingData']["quality"]
                                lr.description = rating_data['ratingData']["description"]
                                lr.delivery_speed = rating_data['ratingData']["deliverySpeed"]
                                lr.customer_service = rating_data['ratingData']["customerService"]
                                lr.timestamp = parse_datetime(rating_data['ratingData']["timestamp"])
                                lr.review = rating_data['ratingData']["review"]
                                lr.save()
                            except IntegrityError as err:
                                print("DB Integrity Error: {0}".format(err))
                                # listing.save()
                        except TypeError:
                            print("bad json in listing " + self.peerID)
                        except Listing.MultipleObjectsReturned:
                            print("Ignoring multiple items with same slug " + self.peerID)
                        except Listing.DoesNotExist:
                            print("Ignoring rating for listing we couldn't find: " + self.peerID)
                    except json.decoder.JSONDecodeError:
                        print("Problem decoding json for listings of peer: " + self.peerID)
            except requests.exceptions.ReadTimeout:
                print("listing peerID " + self.peerID + " timeout")

        for l in self.listing_set.all():
            l.save()

    def update_listings(self, testnet=False):
        import requests
        import json
        IPNS_HOST = settings.IPNS_MAINNET_HOST if not testnet else settings.IPNS_TESTNET_HOST
        OB_HOST = settings.OB_MAINNET_HOST if not testnet else settings.OB_TESTNET_HOST

        listing_url = IPNS_HOST + self.peerID + '/listings.json'

        try:
            response = requests_get_wrap(listing_url)
            if response.status_code == 200:
                # print('BEGIN listing sync' + self.peerID)
                try:
                    for listing_data in json.loads(response.content.decode('utf-8')):
                        # print(self.peerID + ': ' + listing_data['slug'])
                        listing, listing_created = Listing.objects.get_or_create(profile=self,
                                                                                 slug=listing_data['slug'])

                        if listing_created:
                            listing.hash = listing_data['hash']
                            listing.title = listing_data['title']
                            listing.description = listing_data['description']
                            if listing.listingreport_set.count() == 0:
                                listing.nsfw = listing_data['nsfw']
                            # Don't take ratings here

                            listing.price = listing_data['price']['amount']
                            listing.pricing_currency = listing_data['price']['currencyCode']
                            c = ExchangeRate.objects.get(symbol=listing.pricing_currency)
                            listing.price_value = listing.price / float(c.base_unit) / float(c.rate)

                            listing.network = ('mainnet' if not testnet else 'testnet')

                            if "SERVICE" in listing_data['contractType']:
                                listing.contract_type = Listing.SERVICE
                            elif "DIGITAL_GOOD" in listing_data['contractType']:
                                listing.contract_type = Listing.DIGITAL_GOOD
                            elif "PHYSICAL_GOOD" in listing_data['contractType']:
                                listing.contract_type = Listing.PHYSICAL_GOOD
                            elif "CROWD_FUND" in listing_data['contractType']:
                                listing.contract_type = Listing.CROWD_FUND
                            elif "CRYPTOCURRENCY" in listing_data['contractType']:
                                listing.contract_type = Listing.CRYPTOCURRENCY
                            if 'averageRating' in listing_data.keys():
                                listing.rating_average_stale = listing_data['averageRating']
                            if 'ratingCount' in listing_data.keys():
                                listing.rating_count_stale = listing_data['ratingCount']
                            if 'freeShipping' in listing_data.keys():
                                listing.free_shipping = listing_data['freeShipping']
                            listing.active=True
                            listing.sync(testnet=testnet)
                        else:
                            if 'averageRating' in listing_data.keys():
                                listing.rating_average_stale = listing_data['averageRating']
                            if 'ratingCount' in listing_data.keys():
                                listing.rating_count_stale = listing_data['ratingCount']
                            if 'freeShipping' in listing_data.keys():
                                listing.free_shipping = listing_data['freeShipping']
                            listing.active = True
                            listing.sync(testnet=testnet)


                            # print('shipping: ' + str(listing_data['freeShipping']))

                except json.decoder.JSONDecodeError:
                    print("Problem decoding json for listings of peer: " + self.peerID)
                except TypeError:
                    self.listing_set.update(active=False)
                    print("No listings " + self.peerID)

                except KeyError:
                    print("Problem parsing json for listings of peer: " + self.peerID)

        except requests.exceptions.ReadTimeout:
            print("listing peerID " + self.peerID + " timeout")

    # profile
    def get_rank(self):
        try:
            return get_profile_rank(self)
        except:
            print("set a profile ranking function")
            return randint(1, 1000)

    def __str__(self):
        return self.peerID


    def ping(self, testnet=False):
        try:
            OB_HOST = settings.OB_MAINNET_HOST if not testnet else settings.OB_TESTNET_HOST
            health_url = OB_HOST + 'status/' + self.peerID

            peer_response = requests_get_wrap(health_url,timeout=5)
            try:
                return json.loads(peer_response.content.decode('utf-8'))['status'] == 'online'
            except:
                return False
        except:
            return False

    def save(self, *args, **kwargs):
        self.rating_count = self.listingrating_set.all().count()
        r_avg = self.listingrating_set.aggregate(rating_average=Avg('average'))['rating_average']
        self.rating_average = (r_avg if r_avg else 0)
        self.rating_dot = (r_avg * self.rating_count if r_avg else 0)
        if self.listing_set.filter(nsfw=True).count():
            self.nsfw = True
        else:
            self.nsfw = False

        self.rank = self.get_rank()
        self.listing_count = self.listing_set.count()
        self.moderated_items_count = self.moderated_items.count()
        super(Profile, self).save(*args, **kwargs)


class ListingRating(models.Model):
    ratingID = models.CharField(primary_key=True, max_length=46)
    average = models.FloatField(default=0, null=True)
    overall = models.IntegerField(default=0, null=True)
    quality = models.IntegerField(default=0, null=True)
    description = models.IntegerField(default=0, null=True)
    delivery_speed = models.IntegerField(default=0, null=True)
    customer_service = models.IntegerField(default=0, null=True)
    review = models.TextField(default='', blank=True)
    timestamp = models.DateTimeField(null=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    listing = models.ForeignKey('Listing', related_name='ratings', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


    def get_average(self):
        return float(self.overall + self.quality + self.description + self.delivery_speed + self.customer_service) / 5.0

    def save(self, *args, **kwargs):
        self.average = self.get_average()
        super(ListingRating, self).save(*args, **kwargs)
        self.listing.save()


class Listing(models.Model):
    ANY = ''
    PHYSICAL_GOOD = 0
    DIGITAL_GOOD = 1
    SERVICE = 2
    CROWD_FUND = 3
    CRYPTOCURRENCY = 4

    CONTRACT_TYPE_CHOICES = (
        (ANY, _('Any')),
        (PHYSICAL_GOOD, _('Physical Good')),
        (DIGITAL_GOOD, _('Digital Good')),
        (SERVICE, _('Service')),
        #(CROWD_FUND, _('Crowd Fund')),
        (CRYPTOCURRENCY, _('Cryptocurrency')),
    )

    ANY = ''
    NEW = 0
    USED_EXCELLENT = 1
    USED_GOOD = 2
    USED_POOR = 3
    REFURBISHED = 4
    CONDITION_TYPE_CHOICES = (
        (ANY, _('Any')),
        (NEW, _('New')),
        (USED_EXCELLENT, _('Used Exellent')),
        (USED_GOOD, _('Used Good')),
        (USED_POOR, _('Used Poor')),
        (REFURBISHED, _('Refurbished')),
    )

    CONTRACT_TYPE_DICT = dict(CONTRACT_TYPE_CHOICES)
    CONDITION_TYPE_DICT = dict(CONDITION_TYPE_CHOICES)

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    accepted_currencies = models.TextField(blank=True, default='')
    # Array fields will not work with sqlite3, use the text field instead
    # accepted_currencies_array = ArrayField(models.CharField(max_length=5), null=True, blank=True)

    free_shipping = models.TextField(null=True)
    # Array fields will not work with sqlite3, use the text field instead
    #free_shipping = ArrayField(models.CharField(max_length=80), null=True, blank=True)

    tags = models.TextField(blank=True, default='')
    # Array fields will not work with sqlite3, use the text field instead
    # tags_array = ArrayField(models.CharField(max_length=40), null=True, blank=True)

    categories = models.TextField(blank=True, default='')
    # Array fields will not work with sqlite3, use the text field instead
    # categories_array = ArrayField(models.CharField(max_length=80), null=True, blank=True)

    hash = models.TextField(null=True)
    title = models.TextField(null=True)
    slug = models.SlugField(null=True, max_length=256)
    description = models.TextField(null=True)
    signature = models.TextField(null=True)
    contract_type = models.IntegerField(choices=CONTRACT_TYPE_CHOICES, null=True, blank=True)
    condition_type = models.IntegerField(choices=CONDITION_TYPE_CHOICES, null=True, blank=True)
    rating_count = models.IntegerField(default=0, null=False, blank=False)
    rating_average = models.FloatField(default=0, null=False, blank=False)
    rating_count_stale = models.IntegerField(default=0, null=False, blank=False)
    rating_average_stale = models.FloatField(default=0, null=False, blank=False)
    rating_dot = models.FloatField(default=0, null=False, blank=False)
    moderators = models.ManyToManyField(Profile, related_name='moderated_items', blank=True)
    nsfw = models.BooleanField(default=False)
    spam = models.BooleanField(default=False)
    dust = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    network = models.TextField(default='mainnet', null=False, blank=False)
    price = models.BigIntegerField(null=True, blank=True)
    price_value = models.FloatField(null=True, blank=True)
    pricing_currency = models.TextField()

    version = models.IntegerField(null=True, blank=True)
    refund_policy = models.TextField(null=True)

    rank = models.IntegerField(default=0, null=False, blank=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    attempt = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('profile', 'slug',)
        ordering = ['-rank']

    # Listing
    def should_update(self):
        if self.profile.online or True:
            if self.attempt < now() - timedelta(hours=settings.SHORTEST_UPDATE_HOURS):
                return True
            else:
                print("too soon")
                return False
        else:
            print("offline")
            return False

    #should_update = Profile.should_update


    def get_sync_url(self, testnet=False):
        IPNS_HOST = settings.IPNS_MAINNET_HOST if not testnet else settings.IPNS_TESTNET_HOST
        return IPNS_HOST + self.profile_id + '/listings/' + self.slug + '.json'

    # Listing
    def get_rank(self):
        try:
            return get_listing_rank(self)
        except:
            print("Warning, no listing ranking function")
            return randint(1,1000)

    # Listing
    def sync(self, force=True, testnet=False):
        listing_detail_url = self.get_sync_url(testnet)
        print(self.profile_id + "sync : " + self.slug)
        try:
            response = requests_get_wrap(listing_detail_url)
            if response.status_code == 200:
                listing_detail_data = json.loads(response.content.decode('utf-8'))
                listing_data = listing_detail_data['listing']
                signature = listing_detail_data['signature']
                if self.signature == signature and force is False:
                    self.save()
                else:
                    self.signature = signature
                    self.slug = listing_data['slug']
                    metadata = listing_data['metadata']
                    self.version = metadata['version']
                    if "PHYSICAL_GOOD" in metadata['contractType']:
                        self.contract_type = Listing.PHYSICAL_GOOD
                    elif "DIGITAL_GOOD" in metadata['contractType']:
                        self.contract_type = Listing.DIGITAL_GOOD
                    elif "SERVICE" in metadata['contractType']:
                        self.contract_type = Listing.SERVICE
                    self.accepted_currencies = metadata['acceptedCurrencies'][0]
                    # Array fields will not work with sqlite3, use the text field instead
                    # self.accepted_currencies_array = metadata['acceptedCurrencies']
                    self.pricing_currency = metadata['pricingCurrency']

                    item_details = listing_data['item']
                    self.title = item_details['title']
                    if 'tags' in item_details:
                        self.tags = item_details['tags']
                        # Array fields will not work with sqlite3, use the text field instead
                        # self.tags_array = item_details['tags']
                    if 'categories' in item_details:
                        self.categories = item_details['categories']
                        # Array fields will not work with sqlite3, use the text field instead
                        # self.categories_array = item_details['categories']
                    if 'price' in item_details:
                        self.price = item_details['price']

                        c = ExchangeRate.objects.get(symbol=self.pricing_currency)
                        self.price_value = self.price / float(c.base_unit) / float(c.rate)

                    if 'description' in item_details.keys():
                        self.description = item_details['description']

                    if "NEW" in item_details['condition']:
                        self.condition_type = Listing.NEW
                    elif "USED_EXCELLENT" in item_details['condition']:
                        self.condition_type = Listing.USED_EXCELLENT
                    elif "USED_GOOD" in item_details['condition']:
                        self.condition_type = Listing.USED_GOOD
                    elif "USED_POOR" in item_details['condition']:
                        self.condition_type = Listing.USED_POOR
                    elif "REFURBISHED" in item_details['condition']:
                        self.condition_type = Listing.REFURBISHED

                    if "images" in item_details.keys():
                        for i, iHashes in enumerate(item_details['images']):
                            iHashes['index'] = i
                            iHashes['listing'] = self
                            try:
                                li, liCreated = ListingImage.objects.get_or_create(**iHashes)
                                li.save()
                            except ListingImage.MultipleObjectsReturned:
                                print(
                                    'there were multiple images returned with this hash at this index and item, it\'s probably not a werious issue, but it if is, this message will occur more  and more frequently... hacker style')

                    if "moderators" in listing_data:

                        listed_moderators = listing_data['moderators']
                        known_moderators = Profile.objects.filter(pk__in=listed_moderators)
                        known_moderators_pks = [m.pk for m in known_moderators]
                        new_moderators = [m for m in listed_moderators if m not in known_moderators_pks]
                        if len(new_moderators) > 0:
                            for new_pk in new_moderators:
                                try:
                                    new_mod = Profile.objects.get(pk=new_pk)
                                    # new_mod.sync()
                                except Profile.DoesNotExist:
                                    new_mod, new_mod_created = Profile.objects.get_or_create(pk=new_pk)
                                    if new_mod_created:
                                        new_mod.sync(testnet)

                            moderators = Profile.objects.filter(pk__in=listed_moderators)
                        else:
                            moderators = known_moderators

                        self.moderators.set(list(moderators))

                    if "coupons" in listing_data:
                        for c in listing_data['coupons']:
                            pass

                    if "shippingOptions" in listing_data:
                        for s in listing_data['shippingOptions']:
                            S = ShippingOptions.create_from_json(self, s)
                            S.save()

                    self.network = ('mainnet' if not testnet else 'testnet')
                    self.save()



        except json.decoder.JSONDecodeError:
            print("bad json")
        except requests.exceptions.ReadTimeout:
            is_modified = Listing.objects.filter(slug=self.slug, profile=self.profile).update(attempt=timezone.now())
            print("timeout")

    def save(self, *args, **kwargs):
        self.rating_count = self.ratings.all().count()
        r_avg = self.ratings.aggregate(average=Avg('average'))['average']
        self.rating_average = (r_avg if r_avg else 0)
        self.rating_dot = (r_avg * self.rating_count if r_avg else 0)
        if self.price and self.price > 0:
            self.rank = self.get_rank()
        super(Listing, self).save(*args, **kwargs)


class ListingReport(models.Model):
    slug = models.TextField(default='', null=True)
    peerID = models.TextField(default='', null=True)
    reason = models.TextField(default='', null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not hasattr(self, 'listing'):
            print(self.peerID + ' ' + self.slug)
            self.listing = Listing.objects.filter(profile_id=self.peerID, slug__icontains=self.slug)[0]
        if self.reason != 'OKAY':
            Listing.objects.filter(profile_id=self.peerID, slug__icontains=self.slug).update(nsfw=True)

        if os.environ.get('SCAM_OBSCURE_WORD') and self.reason == os.environ.get('SCAM_OBSCURE_WORD'):
            Profile.objects.filter(peerID=self.peerID).update(scam=True)
        if os.environ.get('ILLEGAL_OBSCURE_WORD') and self.reason == os.environ.get('ILLEGAL_OBSCURE_WORD'):
            Profile.objects.filter(peerID=self.peerID).update(illegal_in_us=True)
        super(ListingReport, self).save(*args, **kwargs)


class ShippingOptions(models.Model):

    LOCAL_PICKUP = 0
    FIXED_PRICE = 1

    OPTION_TYPE_CHOICES = (
        (LOCAL_PICKUP, _('Local Pickup')),
        (FIXED_PRICE, _('Fixed Price')),
    )

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    name = models.TextField(null=True)
    option_type = models.IntegerField(choices=OPTION_TYPE_CHOICES, null=True, blank=True)
    regions = models.TextField(blank=True, null=True)
    # Array fields will not work with sqlite3, use the text field instead
    # regions_array = ArrayField(models.CharField(max_length=80), null=True, blank=True)
    service_name = models.TextField(null=True)
    service_price = models.TextField(null=True)
    service_estimated_delivery = models.TextField(null=True)

    @classmethod
    def create_from_json(cls, parent, data):

        if "FIXED_PRICE" in data['type']:
            option = ShippingOptions.FIXED_PRICE
        elif "LOCAL_PICKUP" in data['type']:
            option = ShippingOptions.LOCAL_PICKUP
        c, ccreated = cls.objects.get_or_create(listing=parent,
                                                name=data['name'])
        c.option_type = option
        if len(data['services']) == 1:
            if 'name' in data['services'][0].keys():
                c.service_name = data['services'][0]['name']
            if 'price' in data['services'][0].keys():
                c.service_price = data['services'][0]['price']
            if 'estimatedDelivery' in data['services'][0].keys():
                c.service_estimated_delivery = data['services'][0]['estimatedDelivery']

        c.regions = str(data['regions'])
        # Array fields will not work with sqlite3, use the text field instead
        # c.regions_array = data['regions']
        return c
