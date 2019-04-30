import os
import logging

from django.conf import settings
from django.db import models
from ob.models.listing import Listing
from ob.models.profile import Profile

logger = logging.getLogger(__name__)


class ListingReport(models.Model):
    slug = models.TextField(default='', null=True)
    peerID = models.TextField(default='', null=True)
    reason = models.TextField(default='', null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not hasattr(self, 'listing'):
            logger.info(self.peerID + ' ' + self.slug)
            self.listing = Listing.objects.filter(profile_id=self.peerID,
                                                  slug__icontains=self.slug)[0]
        if self.reason:
            if self.reason == settings.NSFW:
                # Update the listing
                Listing.objects.filter(profile_id=self.peerID,
                                       slug__icontains=self.slug) \
                    .update(nsfw=True)
            elif self.reason == settings.SCAM:
                # Update the profile
                Profile.objects.filter(peerID=self.peerID).update(scam=True)
            elif self.reason == settings.ILLEGAL:
                # Update the profile
                Profile.objects.filter(peerID=self.peerID).update(
                    illegal_in_us=True)
        super(ListingReport, self).save(*args, **kwargs)
