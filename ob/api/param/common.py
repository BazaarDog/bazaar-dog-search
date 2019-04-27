from collections import OrderedDict
from .static import currency_list
from .util import build_options, build_multi_options
from django.utils.translation import ugettext_lazy as _


def try_param_or_zero(value, return_type=int):
    try:
        return return_type(value)
    except (ValueError, TypeError):
        return 0


def try_int_or_zero(s):
    try:
        return int(s)
    except (ValueError, TypeError):
        return 0


def try_true_or_none(p):
    return True if p == 'true' else ''


def get_clear_all_options():
    return [
        {"value": True,
         "label": _("Clear all"),
         "checked": False,
         "default": False
         }
    ]


def get_currency_type_options(p):
    currencies = p
    distinct_currency = currency_list
    return build_multi_options(currencies, distinct_currency)


def get_nsfw_options(p):
    nsfw_param = p
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


def get_network_options(p):
    network = p or 'mainnet'
    network_choices = OrderedDict(
        [('mainnet', _("Main Network")), ('testnet', _("Test Network")), ])
    return build_options(network, network_choices)
