from datetime import timedelta
import logging
from random import randint

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Avg
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from ob.models.profile import Profile

logger = logging.getLogger(__name__)

try:
    from obscure import get_listing_rank, get_profile_rank
except ImportError:
    from custom import get_listing_rank, get_profile_rank

OB_HOST = settings.OB_MAINNET_HOST


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
        # (CRYPTOCURRENCY, _('Cryptocurrency')),
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

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    accepted_currencies = ArrayField(models.CharField(max_length=5),
                                     null=True,
                                     blank=True)
    free_shipping = ArrayField(models.CharField(max_length=80),
                               null=True,
                               blank=True)
    tags = ArrayField(models.CharField(max_length=80),
                      null=True,
                      blank=True)
    categories = ArrayField(models.CharField(max_length=80),
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
            logger.info("Warning, no listing ranking function")
            return randint(1, 1000)

    def parse_metadata(self, listing_data):
        metadata = listing_data.get('metadata')
        self.version = metadata.get('version')
        self.contract_type = getattr(Listing,
                                     metadata.get('contractType'))
        self.accepted_currencies = metadata.get('acceptedCurrencies')
        self.pricing_currency = metadata.get('pricingCurrency')

    # Listing
    def save(self, *args, **kwargs):
        self.rating_count = self.ratings.all().count()
        r_avg = self.ratings.aggregate(average=Avg('average'))['average']
        self.rating_average = (r_avg if r_avg else 0)
        self.rating_dot = (r_avg * self.rating_count if r_avg else 0)
        if self.price and self.price > 0:
            self.rank = self.get_rank()
        super(Listing, self).save(*args, **kwargs)
