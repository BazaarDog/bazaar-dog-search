from django.core.management.base import BaseCommand, CommandError
from ob.models import Profile, ProfileAddress, Listing, Image
from django.utils import timezone
# import the logging library
import logging

from ob.tasks.sync_profile import sync_profile
# Get an instance of a logger
logger = logging.getLogger(__name__)
from ob.util import update_verified

class Command(BaseCommand):
    help = 'load verified'

    def add_arguments(self, parser):

        # Named (optional) arguments
        parser.add_argument(
            '--url',
            dest='url',
            help='verified moderator url',
        )

    def handle(self, *args, **options):

        url = options.get('url')
        update_verified()


