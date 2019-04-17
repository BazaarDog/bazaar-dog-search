from django.core.management.base import BaseCommand
import logging
from ob.util import get_exchange_rates, update_price_values

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update exchange rates, and common values'

    def handle(self, *args, **options):

        get_exchange_rates()
        update_price_values()


