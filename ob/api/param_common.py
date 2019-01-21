from collections import OrderedDict
from .param_util import build_options
from django.utils.translation import ugettext_lazy as _


def get_clear_all_options():
    return [
        {"value": True,
         "label": _("Reset"),
         "checked": False,
         "default": False
         }
    ]


def get_currency_type_options(params):
    if 'acceptedCurrencies' in params.keys():
        currency = params['acceptedCurrencies']
    else:
        currency = ''

    distinct_currency = OrderedDict(
        [
            ('BCH', _('Bitcoin Cash') + ' (BCH)'),
            ('BTC', _('Bitcoin Core') + ' (BTC)'),
            # ('DOGE', 'Dogecoin (DOGE)'),
            # ('ETC', 'Ethereum Classic (ETC)'),
            # ('ETH', 'Ethereum (ETH)'),
            ('LTC', 'Litecoin (LTC)'),
            ('ZEC', 'ZCash (ZEC)'),
            # ('XZC', 'ZCoin (XZC)'),
            # ('ZEN', 'ZenCash (ZEN)'),
            ('', _('Any')),
            # ('TBCH', 'Testnet BCH (TBCH)'),
            # ('TBTC', 'Testnet BTC (TBTC)'),
        ]
    )
    return build_options(currency, distinct_currency)


def get_nsfw_options(params):
    if 'nsfw' in params.keys():
        try:
            if params['nsfw'] == 'true':
                nsfw = True
            elif params['nsfw'] == 'Affirmative':
                nsfw = 'Affirmative'
            elif params['nsfw'] == 'false':
                nsfw = False
            elif params['nsfw'] == '':
                nsfw = ''
            else:
                nsfw = False
        except ValueError:
            nsfw = False
    else:
        nsfw = False

    nsfw_choices = OrderedDict(
        [
            (False, _('Hide')),
            (True, _('Show')),
            ('Affirmative', _('Only NSFW'))
        ]
    )

    return build_options(nsfw, nsfw_choices)
