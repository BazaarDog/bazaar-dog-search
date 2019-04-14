from datetime import timedelta
import ipaddress
import json
import os
from random import randint
import requests
from lxml import etree as lxmletree

from django.conf import settings
from django.db import models
from django.db.models import Count, Sum, Avg, F
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField

from django.dispatch import receiver

from urllib3.exceptions import SubjectAltNameWarning



requests.packages.urllib3.disable_warnings(SubjectAltNameWarning)

OB_HOST = settings.OB_MAINNET_HOST
IPNS_HOST = settings.IPNS_MAINNET_HOST
OB_INFO_URL = OB_HOST + 'peerinfo/'

try:
    from obscure import get_listing_rank, get_profile_rank
except ImportError:
    from custom import get_listing_rank, get_profile_rank


def try_assign(key, data):
    if key in data.keys():
        return data[key]


class ExchangeRate(models.Model):
    symbol = models.TextField(null=True)
    rate = models.FloatField(default=0)
    base_unit = models.IntegerField(default=100)


class ListingImage(models.Model):
    listing = models.ForeignKey('Listing',
                                related_name='images',
                                on_delete=models.CASCADE)
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

    profile = models.ForeignKey('Profile',
                                related_name='addresses',
                                on_delete=models.CASCADE)
    address = models.TextField(blank=True, default='')
    address_type = models.IntegerField(choices=ADDRESS_TYPE_CHOICES,
                                       null=True,
                                       blank=True)
    created = models.DateTimeField(auto_now_add=True)


class ProfileSocial(models.Model):
    profile = models.ForeignKey('Profile',
                                related_name='social',
                                on_delete=models.CASCADE)
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
    header = models.ForeignKey(Image, related_name='profile_header', null=True,
                               on_delete=models.CASCADE)
    avatar = models.ForeignKey(Image, related_name='profile_avatar', null=True,
                               on_delete=models.CASCADE)
    network = models.TextField(default='mainnet', null=False, blank=False)
    user_agent = models.TextField(blank=True, default='')
    location = models.TextField(blank=True, default='')
    short_description = models.TextField(blank=True, default='')
    moderator = models.BooleanField(default=False)
    moderator_description = models.TextField(default='')
    moderator_terms = models.TextField(default='')
    moderator_languages = models.TextField(default='')
    moderator_languages_array = ArrayField(models.CharField(max_length=10),
                                           null=True,
                                           blank=True)
    moderator_accepted_currencies_array = ArrayField(models.CharField(max_length=10),
                                                     null=True, blank=True)

    moderator_fee_type = models.IntegerField(choices=MODERATOR_FEE_TYPE_CHOICES,
                                             default=0)
    moderator_fee_percentage = models.FloatField(default=0, null=False,
                                                 blank=False)
    moderator_fee_fixed_currency = models.TextField(default='')
    moderator_fee_fixed_amount = models.FloatField(default=0, null=False,
                                                   blank=False)

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
    moderated_items_count = models.IntegerField(default=0, null=False,
                                                blank=False)

    rating_count = models.IntegerField(default=0, null=False, blank=False)
    rating_average = models.FloatField(default=0, null=False, blank=False)
    rating_dot = models.FloatField(default=0, null=False, blank=False)

    connection_type = models.IntegerField(choices=CONNECTION_TYPE_CHOICES,
                                          default=OFFLINE)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    attempt = models.DateTimeField(auto_now=True)
    was_online = models.DateTimeField(auto_now=False, null=True)
    pinged = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rank']

    def get_seralized_record(self):
        from ob.util import get
        try:
            profile_url = OB_HOST + self.peerID
            peer_response = get(profile_url)
            if peer_response.status_code == 200:
                peer_data = json.loads(peer_response.content.decode('utf-8'))
                return peer_data['serializedRecord']
            else:
                print('Error getting seralized record {}'.format(peer_response))
        except IndexError:
            print('index error getting serialized record')

    # profile

    def should_update(self):

        if self.online or True:
            if self.serialized_record is not self.get_seralized_record():
                if self.attempt < now() - timedelta(
                        hours=settings.SHORTEST_UPDATE_HOURS):
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

    def get_neighbors(self):
        try:
            from ob.util import get
            closestpeers_url = OB_HOST + 'closestpeers/' + self.peerID
            peer_response = get(closestpeers_url)
            if peer_response.status_code == 200:
                peer_data = json.loads(peer_response.content.decode('utf-8'))
                return peer_data

        except IndexError:
            print('index error getting address')


    # profile
    def get_rank(self):
        try:
            return get_profile_rank(self)
        except:
            print("set a profile ranking function")
            return randint(1, 1000)

    def __str__(self):
        return self.peerID

    def ping(self):
        try:
            OB_HOST = settings.OB_MAINNET_HOST
            health_url = OB_HOST + 'status/' + self.peerID
            from ob.util import get
            peer_response = get(health_url, timeout=5)
            try:
                return json.loads(peer_response.content.decode('utf-8'))[
                           'status'] == 'online'
            except:
                return False
        except:
            return False

    def save(self, *args, **kwargs):
        self.rating_count = self.listingrating_set.all().count()
        r_avg = self.listingrating_set.aggregate(rating_average=Avg('average'))[
            'rating_average']
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
    listing = models.ForeignKey('Listing', related_name='ratings',
                                on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_average(self):
        return float(
            self.overall + self.quality + self.description +
            self.delivery_speed + self.customer_service) / 5.0

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
        # (CROWD_FUND, _('Crowd Fund')),
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
    accepted_currencies_array = ArrayField(models.CharField(max_length=5), null=True, blank=True)
    free_shipping = ArrayField(models.CharField(max_length=80),
                               null=True,
                               blank=True)
    tags_array = ArrayField(models.CharField(max_length=80),
                            null=True,
                            blank=True)
    categories_array = ArrayField(models.CharField(max_length=80),
                                  null=True,
                                  blank=True)
    hash = models.TextField(null=True)
    title = models.TextField(null=True)
    slug = models.SlugField(null=True, max_length=256)
    description = models.TextField(null=True)
    signature = models.TextField(null=True)
    contract_type = models.IntegerField(choices=CONTRACT_TYPE_CHOICES,
                                        null=True, blank=True)
    condition_type = models.IntegerField(choices=CONDITION_TYPE_CHOICES,
                                         null=True, blank=True)
    rating_count = models.IntegerField(default=0, null=False, blank=False)
    rating_average = models.FloatField(default=0, null=False, blank=False)
    rating_count_stale = models.IntegerField(default=0, null=False, blank=False)
    rating_average_stale = models.FloatField(default=0, null=False, blank=False)
    rating_dot = models.FloatField(default=0, null=False, blank=False)
    moderators = models.ManyToManyField(Profile, related_name='moderated_items',
                                        blank=True)
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
        if self.profile.online:
            hrs = settings.SHORTEST_UPDATE_HOURS
            if self.attempt < now() - timedelta(hours=hrs):
                return True
        return False

    def get_sync_url(self):
        return OB_HOST + 'listing/' + self.profile_id + '/' + self.slug

    # 
    def get_rank(self):
        try:
            return get_listing_rank(self)
        except:
            print("Warning, no listing ranking function")
            return randint(1, 1000)

    # Listing
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
            self.listing = Listing.objects.filter(profile_id=self.peerID,
                                                  slug__icontains=self.slug)[0]
        if self.reason != 'OKAY':
            Listing.objects.filter(profile_id=self.peerID,
                                   slug__icontains=self.slug).update(nsfw=True)

        if os.getenv('SCAM_OBSCURE_WORD') and self.reason == os.getenv(
                'SCAM_OBSCURE_WORD'):
            Profile.objects.filter(peerID=self.peerID).update(scam=True)
        if os.getenv('ILLEGAL_OBSCURE_WORD') and self.reason == os.getenv(
                'ILLEGAL_OBSCURE_WORD'):
            Profile.objects.filter(peerID=self.peerID).update(
                illegal_in_us=True)
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
    option_type = models.IntegerField(choices=OPTION_TYPE_CHOICES, null=True,
                                      blank=True)
    regions_array = ArrayField(models.CharField(max_length=80), null=True, blank=True)
    service_name = models.TextField(null=True)
    service_price = models.TextField(null=True)
    service_estimated_delivery = models.TextField(null=True)

    @classmethod
    def create_from_json(cls, parent, data):

        option = getattr(ShippingOptions, data['type'])
        c, ccreated = cls.objects.get_or_create(listing=parent,
                                                name=data['name'])
        c.option_type = option
        if len(data['services']) == 1:
            if 'name' in data['services'][0].keys():
                c.service_name = data['services'][0]['name']
            if 'price' in data['services'][0].keys():
                c.service_price = data['services'][0]['price']
            if 'estimatedDelivery' in data['services'][0].keys():
                c.service_estimated_delivery = data['services'][0][
                    'estimatedDelivery']

        c.regions_array = data['regions']
        return c
