from django.conf import settings
from django.db.models import F, Count
from django.utils.timezone import now
from ob.models import Profile, Listing, ExchangeRate
import json
import requests
from ob.bootstrap.known_nodes import peerId_list

from pathlib import Path


def get(url, timeout=settings.CRAWL_TIMEOUT):
    if 'https' in url:
        if Path(settings.OB_CERTIFICATE).is_file():
            return requests.get(url,
                                timeout=timeout,
                                auth=settings.OB_API_AUTH,
                                verify=settings.OB_CERTIFICATE)
        else:
            print(
                "couldn't find ssl cert for a secure "
                "connection to openbazaar-go server... ")
            raise Exception
    else:
        return requests.get(url,
                            timeout=settings.CRAWL_TIMEOUT)


def requests_post_wrap(url, data):
    print(url)
    if 'https' in url:
        if Path(settings.OB_CERTIFICATE).is_file():
            return requests.post(url,
                                 data=data,
                                 timeout=settings.CRAWL_TIMEOUT,
                                 auth=settings.OB_API_AUTH,
                                 verify=settings.OB_CERTIFICATE
                                 )
        else:
            raise Exception
    else:
        return requests.post(url,
                             data=data,
                             timeout=settings.CRAWL_TIMEOUT)

def bootstrap():
    for peerId in peerId_list:
        p, pc = Profile.objects.get_or_create(pk=peerId)
        if p.should_update():
            try:
                p.sync(testnet=False)
            except requests.exceptions.ReadTimeout:
                print("read timeout")
        else:
            print('skipping profile')


def moving_average_speed(profile):
    # Keep track of how quickly a peer resolves
    speed_rank = settings.CRAWL_TIMEOUT * 1e6
    new_rank = (profile.speed_rank + speed_rank) / 2.0
    Profile.objects.filter(pk=profile.peerID).update(speed_rank=new_rank,
                                                     attempt=now())
    print("peerID " + profile.peerID + " timeout")


def get_exchange_rates():
    rates_url = settings.OB_MAINNET_HOST + 'exchangerates/BCH'
    response = requests.get(rates_url,
                            timeout=settings.CRAWL_TIMEOUT,
                            auth=settings.OB_API_AUTH,
                            verify=settings.OB_CERTIFICATE
                            )
    if response.status_code == 200:
        forex_data = json.loads(response.content.decode('utf-8'))
        for symbol, rate in forex_data.items():
            updated = ExchangeRate.objects.filter(symbol__exact=symbol).update(
                rate=rate)
            if updated == 0:
                fx, fx_c = ExchangeRate.objects.get_or_create(symbol=symbol)
                fx.rate = rate
                fx.save()


def update_price_values():
    # Listing.update(stories_filed=F('stories_filed') + 1)
    qs_currency_count = Listing.objects.values('pricing_currency') \
        .annotate(cur_count=Count('pricing_currency')) \
        .filter(cur_count__gte=1).order_by('-cur_count')
    distinct_currencies = [v['pricing_currency'] for v in
                           list(qs_currency_count)]
    for c_symbol in distinct_currencies:
        try:
            c = ExchangeRate.objects.get(symbol=c_symbol)
            a = Listing.objects.filter(pricing_currency=c_symbol).update(
                price_value=F('price') / float(c.base_unit) / float(c.rate))
        except ExchangeRate.DoesNotExist:
            print(
                'could not update price_values of ' + c_symbol + ' listings')


def update_verified():
    verified_url = 'https://search.ob1.io/verified_moderators'
    response = requests.get(verified_url)
    if response.status_code == 200:
        from ob.models import Profile
        verified_data = json.loads(response.content.decode('utf-8'))
        verified_pks = [p['peerID'] for p in verified_data['moderators']]
        Profile.objects.filter().update(verified=False)
        Profile.objects.filter(pk__in=verified_pks).update(verified=True)
