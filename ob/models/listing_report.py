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

        # This is a hack to handle the case where a report is sourced from the
        # profile listing search result
        if not hasattr(self, 'listing'):
            logger.info(self.peerID + ' ' + self.slug)
            self.listing = Listing.objects.filter(profile_id=self.peerID,
                                                  slug=self.slug)[0]
        if self.reason:
            self.handle_report()

        super(ListingReport, self).save(*args, **kwargs)

    def handle_report(self):
        actions = {settings.NSFW: self.mark_listing_nsfw(),
                   settings.SCAM: self.mark_peer_scam(),
                   settings.ILLEGAL: self.mark_peer_illegal()}
        if self.reason in actions:
            actions[self.reason]

    def mark_listing_nsfw(self):
        Listing.objects.filter(profile_id=self.peerID,
                               slug=self.slug).update(nsfw=True)

    def mark_peer_scam(self):
        Profile.objects.filter(peerID=self.peerID).update(scam=True)

    def mark_peer_illegal(self):
        Profile.objects.filter(peerID=self.peerID).update(illegal_in_us=True)
