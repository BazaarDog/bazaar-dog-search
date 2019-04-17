import logging

from django.core.management.base import BaseCommand, CommandError

from ob.models.profile import Profile
from ob.models.listing_report import ListingReport as ListingR

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'blacklist profiles'

    def add_arguments(self, parser):

        # Named (optional) arguments
        parser.add_argument(
            '--peer',
            dest='peer',
            help='Peer to Blacklist',
        )
        # Named (optional) argument
        parser.add_argument(
            '--reason',
            dest='reason',
            help='reason for blacklisting',
        )

    def handle(self, *args, **options):
        peerID = options['peer']
        reason = options['reason']

        p = Profile.objects.get(pk=peerID)
        if reason.lower() == 'scam':
            p.scam = True
            p.save()
        for listing in p.listing_set.all():
            lr, lrc = ListingR.objects.get_or_create(listing=listing,
                                                     reason=reason,
                                                     slug=listing.slug,
                                                     peerID=listing.profile_id)
            lr.save()
