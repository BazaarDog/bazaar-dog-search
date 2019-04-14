from django.core.management.base import BaseCommand, CommandError
from ob.models import Profile, ProfileAddress, Listing, Image
from django.utils import timezone
# import the logging library
import logging

from ob.tasks.sync_profile import sync_profile
# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'crawl neighbors'

    def add_arguments(self, parser):

        # Named (optional) arguments
        parser.add_argument(
            '--newer',
            dest='only_new',
            help='Only load new items',
        )

    def handle(self, *args, **options):

        if options['only_new']:
            only_new = True
        else:
            only_new = False

        import json
        import requests
        from time import sleep
        all_pks = [v[0] for v in Profile.objects.filter().values_list('pk')]
        base_url = 'http://127.0.0.1:4002/'
        ipns_url = base_url + 'ipns/'
        peers_url = base_url + 'ob/peers'
        crawl_url = base_url + 'ob/closestpeers'
        info_url = base_url + 'ob/peerinfo/'
        response = requests.get(peers_url)
        if response.status_code == 200:
            for peerID in json.loads(response.content.decode('utf-8')):

                if only_new:
                    crawl_this_node = peerID not in all_pks
                else:
                    crawl_this_node = True

                if crawl_this_node:
                    try:
                        p = Profile.objects.get(pk=peerID)
                        sync_profile(p)
                    except Profile.DoesNotExist:
                        p = Profile(pk=peerID)
                        sync_profile(p)

        else:
            return None
