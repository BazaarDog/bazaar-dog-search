from django.core.management.base import BaseCommand, CommandError
from ob.models import Profile, Listing
from django.utils import timezone
# import the logging library
import logging
from requests.exceptions import ReadTimeout

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'bootstrap vendor'

    def handle(self, *args, **options):
        import json
        import requests
        from time import sleep
        from custom import the_champions_of_decentralized_commerce

        from ob.util import get_exchange_rates
        get_exchange_rates()

        qs = Profile.objects.filter(network='mainnet', online=True).exclude(name='')

        try:
            known_pks = [p['peerID'] for p in qs.values('peerID')]
            for peerID in the_champions_of_decentralized_commerce:
                if peerID not in known_pks:
                    print(peerID)
                    p, profile_created = Profile.objects.get_or_create(pk=peerID)
                    if profile_created or p.should_update():
                        p.sync(testnet=False)
                    else:
                        print('skipping profile')
        except ReadTimeout:
            pass
        print("Successfully bootstraped peers")

        from django.utils.timezone import now
        Profile.objects.filter().update(was_online=now())
