from django.core.management.base import BaseCommand, CommandError
from ob.models import Profile, Listing
from django.utils import timezone
import logging
from requests.exceptions import ReadTimeout

from ob.tasks.sync_profile import sync_profile

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'bootstrap vendor'

    def handle(self, *args, **options):
        from custom import good_nodes

        from ob.util import get_exchange_rates, update_price_values, update_verified
        get_exchange_rates()

        qs = Profile.objects.filter(network='mainnet', online=True).exclude(name='')

        try:
            known_pks = [p['peerID'] for p in qs.values('peerID')]
            for peerID in good_nodes:
                if peerID not in known_pks:
                    logger.debug(peerID)
                    p, profile_created = Profile.objects.get_or_create(pk=peerID)
                    sync_profile(p)

        except ReadTimeout:
            pass
        logger.debug("Successfully bootstraped peers")
        update_verified()
        update_price_values()
        from django.utils.timezone import now
        Profile.objects.filter().update(was_online=now())
