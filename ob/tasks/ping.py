#!/usr/bin/env python

import aiohttp
import asyncio
import async_timeout
import json
import logging
from pathlib import Path
from urllib.parse import urljoin, urldefrag
from ob.models import Profile
from django.conf import settings
from concurrent.futures._base import TimeoutError
from django.utils.timezone import now
from datetime import timedelta

logger = logging.getLogger(__name__)

pinged_peers = {}

OB_HOST = settings.OB_MAINNET_HOST
base_url = OB_HOST + 'status/'

auth = aiohttp.BasicAuth(settings.OB_API_AUTH[0],settings.OB_API_AUTH[1])

async def get_ping(peerID):
    async with aiohttp.ClientSession() as session:
        try:
            with async_timeout.timeout(20):
                async with session.get(base_url+peerID,
                                       timeout=20,
                                       auth=auth,
                                       ssl=False
                                       ) as response:
                    #logger.info('{} is {}'.format(peerID, await response.json()))
                    try:
                        if response.status == 200:
                            pinged_peers[peerID] = (await response.json())['status'] == 'online'
                        else:
                            del pinged_peers[peerID]
                    except TimeoutError:
                        del pinged_peers[peerID]
        except TimeoutError:
            pass #del pinged_peers[peerID]


async def handle_task(task_id, work_queue):
    while not work_queue.empty():
        queue_id = await work_queue.get()
        if not queue_id in pinged_peers.keys():
            return await get_ping(queue_id)

def ping_many(peerIDs):

    q = asyncio.Queue()

    [q.put_nowait(peerID) for peerID in peerIDs]

    if asyncio.get_event_loop().is_closed():
        asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    tasks = [handle_task(task_id, q) for task_id in range(len(peerIDs))]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    return pinged_peers


def ping_query_set(peerIDs):
    pinged_peers = ping_many(peerIDs)
    online_nodes = list(d for d, s in pinged_peers.items() if s)
    on = Profile.objects.filter(peerID__in=online_nodes).update(online=True, pinged=now(), was_online=now())
    off = Profile.objects.filter(peerID__in=peerIDs).exclude(peerID__in=online_nodes).update(online=False, pinged=now())
    logger.info('there were {} peers online and {} peers offline'.format(on,off))


def ping_offline():
    some_time_ago = now() - timedelta(minutes=100)
    a_long_time_ago = now() - timedelta(days=28)
    qs = Profile.objects.filter(online=False,
                                modified__gt=a_long_time_ago,
                                pinged__lt=some_time_ago).values_list('pk', flat=True).order_by('?')
    qs = list(qs)[:300] # vector length should be an argument, didn't play well with AWS lambda
    if len(qs) > 0:
        ping_query_set(qs)


def ping_online(number=200):

    some_time_ago = now() - timedelta(minutes=60) # try not to hit nodes online in last hour
    qs = Profile.objects.filter(online=True,
                                pinged__lt=some_time_ago).values_list('pk', flat=True).order_by('?')#[:number]
    qs = list(qs)[:100] # vector length should be an argument, didn't play well with AWS lambda
    if len(qs) > 0:
        ping_query_set(qs)
