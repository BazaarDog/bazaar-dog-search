from collections import OrderedDict
from .static import currency_list
from .util import build_options, build_multi_options
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
        currencies = params.getlist('acceptedCurrencies')
    else:
        currencies = []
    distinct_currency = currency_list
    return build_multi_options(currencies, distinct_currency)


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


def get_network_options(params):

    network = params['network'] if 'network' in params.keys() else 'mainnet'
    network_choices = OrderedDict([('mainnet', _("Main Network")), ('testnet', _("Test Network")), ])
    return build_options(network, network_choices)
