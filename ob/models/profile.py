from datetime import timedelta
import json
import logging
from random import randint

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Avg
from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from ob.models.image import Image
from ob.models.listing_rating import ListingRating

try:
    from obscure import get_listing_rank, get_profile_rank
except ImportError:
    from custom import get_listing_rank, get_profile_rank

logger = logging.getLogger(__name__)

OB_HOST = settings.OB_MAINNET_HOST
IPNS_HOST = settings.IPNS_MAINNET_HOST
OB_INFO_URL = OB_HOST + 'peerinfo/'


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
    moderator_languages = ArrayField(models.CharField(max_length=10),
                                     null=True,
                                     blank=True)
    moderator_accepted_currencies = ArrayField(models.CharField(max_length=10),
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
                logger.info(
                    'Error getting seralized record {}'.format(peer_response))
        except IndexError:
            logger.info('index error getting serialized record')

    def should_update(self):

        if self.online:
            if self.serialized_record is not self.get_seralized_record():
                if self.attempt < now() - timedelta(
                        hours=settings.SHORTEST_UPDATE_HOURS):
                    return True
                else:
                    logger.info("too soon")
                    return False
            else:
                Profile.objects.filter(pk=self.peerID).update(modified=now())
                logger.info("no change")
                return False
        else:
            logger.info("offline")
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
            logger.info('index error getting address')

    def get_rank(self):
        try:
            return get_profile_rank(self)
        except:
            logger.info("set a profile ranking function")
            return randint(1, 1000)

    def ping(self):
        try:
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

    def __str__(self):
        return self.peerID

    def moving_average_speed(self, speed_rank):
        # Keep track of how quickly a peer resolves
        new_rank = (self.speed_rank * 0.1) + (speed_rank * 0.9)
        Profile.objects.filter(pk=self.peerID).update(speed_rank=new_rank,
                                                      attempt=now())
        logger.info("peerID " + self.peerID + " timeout")

    def has_tor(self):
        return self.addresses.filter(address_type=self.TOR).exists()

    def has_clearnet(self):
        return self.addresses.filter(
            address_type__in=[self.DUAL, self.CLEAR]
        ).exists()
