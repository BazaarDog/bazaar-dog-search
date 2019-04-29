import logging

from django.core.management.base import BaseCommand, CommandError

from ob.util import update_verified

logger = logging.getLogger(__name__)


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
        c, url = update_verified(verified_url=url)
        self.stdout.write(
            "Updated {} verified vendors from {}".format(c, url)
        )
