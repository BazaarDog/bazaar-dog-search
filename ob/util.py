from django.core import exceptions
from importlib import import_module
from django.conf import settings
from django.db.models import F, Count
from ob.models import Listing, ExchangeRate
import json, requests
from requests.exceptions import ReadTimeout

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
            except ReadTimeout:
                print("read timeout")
        else:
            print('skipping profile')


def update_dog_following():
    following_url = settings.OB_MAINNET_HOST + 'following'
    response = requests.get(following_url,
                            timeout=settings.CRAWL_TIMEOUT,
                            auth=settings.OB_API_AUTH,
                            verify=settings.OB_CERTIFICATE
                            )
    if response.status_code == 200:
        from ob.models import Profile
        following_data = json.loads(response.content.decode('utf-8'))
        Profile.objects.filter(pk__in=following_data).update(dog_follows=True)
        Profile.objects.filter().exclude(pk__in=following_data).update(dog_follows=False)
        Profile.objects.filter(pk='QmTBVgfJ4jZdyUhdHYi73oBjupSHv7bRNjMcVYupC13sJh').update(dog_follows=True)


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
            print(c)
        except:
            print('could not update price_values of ' + c_symbol + ' denominated listings')


CLASS_PATH_ERROR = 'bazaar-dog-search is unable to interpret settings value for %s. ' \
                   '%s should be in the form of a tupple: ' \
                   '(\'path.to.models.Class\', \'app_label\').'


def get_model_string(model_name):
    """
    Returns the model string notation Django uses for lazily loaded ForeignKeys
    (eg 'auth.User') to prevent circular imports.

    This is needed to allow our crazy custom model usage.
    """
    setting_name = 'OB_%s_MODEL' % model_name.upper().replace('_', '')
    class_path = getattr(settings, setting_name, None)

    if not class_path:
        return 'auction.%s' % model_name
    elif isinstance(class_path, basestring):
        parts = class_path.split('.')
        try:
            index = parts.index('models') - 1
        except ValueError:
            raise exceptions.ImproperlyConfigured(CLASS_PATH_ERROR % (
                setting_name, setting_name))
        app_label, model_name = parts[index], parts[-1]
    else:
        try:
            class_path, app_label = class_path
            model_name = class_path.split('.')[-1]
        except:
            raise exceptions.ImproperlyConfigured(CLASS_PATH_ERROR % (
                setting_name, setting_name))

    return '%s.%s' % (app_label, model_name)


def update_verified():
    verified_url = 'https://search.ob1.io/verified_moderators'
    response = requests.get(verified_url)
    if response.status_code == 200:
        from ob.models import Profile
        verified_data = json.loads(response.content.decode('utf-8'))
        verified_pks = [p['peerID'] for p in verified_data['moderators']]
        Profile.objects.filter().update(verified=False)
        Profile.objects.filter(pk__in=verified_pks).update(verified=True)


