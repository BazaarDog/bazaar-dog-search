from datetime import timedelta
import logging
import random
from requests.exceptions import ReadTimeout
from time import sleep

from django.db.models import Count
from django.conf import settings
from django.utils.timezone import now

from ob.models import Profile, Listing
from ob.tasks.sync_profile import sync_profile

logger = logging.getLogger(__name__)


def find_nodes():
    # network = ('testnet' if testnet else 'mainnet')

    qs = Profile.objects.filter(network='mainnet', online=True).exclude(name='')
    count = qs.aggregate(count=Count('pk'))['count']
    random.seed(now())
    random_index = random.randint(0, count - 1)
    p = Profile.objects.all()[random_index]
    try:
        new_count = 0
        random_neighbors = p.get_neighbors()
        known_pks = [p['peerID'] for p in qs.values('peerID')]
        for peerID in random_neighbors:
            if peerID not in known_pks:
                p, profile_created = Profile.objects.get_or_create(pk=peerID)
                if profile_created or p.should_update():
                    new_count += 1
                    sync_profile(p)
                else:
                    logger.info('skipping profile')
    except ReadTimeout:
        pass
    logger.info("Successfully crawled got " + str(new_count) + " more peers")


def sync_an_empty_peer(testnet=False):
    network = ('testnet' if testnet else 'mainnet')
    while True:
        count = Profile.objects.filter(name='', network=network).aggregate(count=Count('pk'))['count']
        random.seed(now())
        if count > 0:
            random_index = random.randint(0, count - 1)
            p = Profile.objects.filter(name='', network=network)[random_index]
            if p.should_update():
                try:
                    p.sync(testnet)
                except ReadTimeout:
                    logger.info("read timeout")
            else:
                logger.info('skipping profile')
            logger.info("Successfully crawled an empty peer")
        sleep(60)


def sync_a_known_peer():
    some_time_ago = now() - timedelta(hours=24)
    a_long_time_ago = now() - timedelta(days=14)
    qs = Profile.objects.filter(modified__lt=some_time_ago, modified__gt=a_long_time_ago, online=True,
                                network='mainnet').exclude(name='')
    count = qs.aggregate(count=Count('pk'))['count']
    if count > 0:
        random.seed(now())
        random_index = random.randint(0, count - 1)
        p = qs[random_index]
        logger.info(p.peerID + ' ' + p.network)
        if p.should_update():
            try:
                p.sync()
            except ReadTimeout:
                logger.info("read timeout")
        else:
            logger.info('skipping profile')
        logger.info("Successfully crawled a known peer")
    else:
        logger.info("All caught up")


def sync_an_empty_listing(testnet=False):
    network = ('testnet' if testnet else 'mainnet')
    while True:
        qs = Listing.objects.filter(network=network, images__isnull=True)
        count = qs.aggregate(count=Count('pk'))['count']
        if count > 0:
            random.seed(now())
            random_index = random.randint(0, count - 1)
            l = qs[random_index]
            if l.should_update():
                try:
                    l.sync(testnet)
                except ReadTimeout:
                    logger.info("read timeout")
            else:
                logger.info('skipping profile')
            logger.info("Successfully crawled an empty listing")


def sync_a_listing(testnet=False):
    network = ('testnet' if testnet else 'mainnet')
    while True:
        some_time_ago = now() - timedelta(hours=24)
        qs = Listing.objects.filter(modified__lt=some_time_ago)
        count = qs.aggregate(count=Count('pk'))['count']
        if count > 0:
            random.seed(now())
            random_index = random.randint(0, count - 1)
            l = Listing.objects.filter(modified__lt=some_time_ago)[random_index]
            if l.should_update():
                try:
                    l.sync(testnet)
                except ReadTimeout:
                    logger.info("read timeout")
            else:
                logger.info('skipping profile')
            logger.info("Successfully crawled a listing")
        sleep(10)
