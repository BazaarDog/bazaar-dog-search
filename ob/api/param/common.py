from collections import OrderedDict
from .static import currency_list
from .util import build_options, build_multi_options
from django.utils.translation import ugettext_lazy as _


def get_clear_all_options():
    return [
        {"value": True,
         "label": _("Clear all"),
         "checked": False,
         "default": False
         }
    ]


def get_currency_type_options(params):
    currencies = params.getlist('acceptedCurrencies') or []
    distinct_currency = currency_list
    return build_multi_options(currencies, distinct_currency)


def get_nsfw_options(params):
    nsfw_param = params.get('nsfw')
    nsfw_options = {
        'true': True,
        'Affirmative': 'Affirmative',
        'false': False
    }
    if nsfw_param in nsfw_options:
        nsfw = nsfw_options.get(nsfw_param)
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


def get_network_options(params):
    network = params.get('network') or 'mainnet'
    network_choices = OrderedDict(
        [('mainnet', _("Main Network")), ('testnet', _("Test Network")), ])
    return build_options(network, network_choices)
