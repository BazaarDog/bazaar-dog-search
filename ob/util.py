from django.conf import settings
from django.db.models import F, Count
from ob.models import Listing, ExchangeRate
import json
import requests

def bootstrap(more=False):
    if more:
        from ob.phixtures.good_nodes import more_nodes as good_nodes
    else:
        from ob.phixtures.good_nodes import good_nodes

    from ob.models import Profile
    for p in good_nodes:
        p, pc = Profile.objects.get_or_create(pk=p)
        if p.should_update():
            try:
                p.sync(testnet=False)
            except requests.exceptions.ReadTimeout:
                print("read timeout")
        else:
            print('skipping profile')

def get_exchange_rates():
    rates_url = settings.OB_MAINNET_HOST + 'exchangerates/'
    response = requests.get(rates_url,
                            timeout=settings.CRAWL_TIMEOUT,
                            auth=settings.OB_API_AUTH,
                            verify=settings.OB_CERTIFICATE
                            )
    if response.status_code == 200:
        forex_data = json.loads(response.content.decode('utf-8'))
        for k, v in forex_data.items():
            updated = ExchangeRate.objects.filter(symbol__exact=k).update(rate=v)
            if updated == 0:
                fx, fx_c = ExchangeRate.objects.get_or_create(symbol=k)
                fx.rate = v
                fx.save()


def update_price_values():
    # Listing.update(stories_filed=F('stories_filed') + 1)
    qs_currency_count = Listing.objects.values('pricing_currency')\
        .annotate(cur_count=Count('pricing_currency'))\
        .filter(cur_count__gte=1).order_by('-cur_count')
    distinct_currencies = [v['pricing_currency'] for v in list(qs_currency_count)]
    for c_symbol in distinct_currencies:
        try:
            c = ExchangeRate.objects.get(symbol=c_symbol)
            a = Listing.objects.filter(pricing_currency=c_symbol).update(
                price_value=F('price') / float(c.base_unit) / float(c.rate))
        except ExchangeRate.DoesNotExist:
            print('could not update price_values of ' + c_symbol + ' denominated listings')


def update_verified():
    verified_url = 'https://search.ob1.io/verified_moderators'
    response = requests.get(verified_url)
    if response.status_code == 200:
        from ob.models import Profile
        verified_data = json.loads(response.content.decode('utf-8'))
        verified_pks = [p['peerID'] for p in verified_data['moderators']]
        Profile.objects.filter().update(verified=False)
        Profile.objects.filter(pk__in=verified_pks).update(verified=True)


