from django.core.management.base import BaseCommand
import logging
from ob.tasks.ping import ping_offline, ping_online

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Ping a sample of nodes to see who is online'

    def handle(self, *args, **options):
        ping_offline()
        ping_online()


