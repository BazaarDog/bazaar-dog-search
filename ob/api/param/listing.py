from collections import OrderedDict

from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import ugettext_lazy as _

from ob.models.listing import Listing
from ob.models.profile import Profile
from .util import build_options
from .common import get_nsfw_options, get_currency_type_options, \
    get_clear_all_options, get_network_options, try_param_or_zero, \
    try_true_or_none, try_int_or_zero, try_int_or_blank
from .static import country_list


def get_listing_options(params):
    region = params.get('shipping') if params.get('shipping') else 'any'
    currency_type = params.getlist('acceptedCurrencies') or []
    available_options = [
        ("acceptedCurrencies", {
            "type": "checkbox",
            "label": _("Accepted Currencies"),
            "options": get_currency_type_options(currency_type)
        }),
        ("moderator_verified", {
            "type": "checkbox",
            "label": _("Verified Moderator"),
            "options": get_moderator_verified_options(
                params.get('moderator_verified')
            )
        }),
        ("moderator_count", {
            "type": "radio",
            "label": _("Moderators Available"),
            "options": get_moderator_options(
                params.get('moderator_count')
            )
        }),
        ("nsfw", {
            "type": "radio",
            "label": _("Adult Content"),
            "options": get_nsfw_options(
                params.get('nsfw')
            )
        }),
        ("condition_type", {
            "type": "radio",
            "label": _("Condition"),
            "options": get_condition_type_options(
                params.get('condition_type')
            )
        }),
        ("rating", {
            "type": "radio",
            "label": _("Rating"),
            "options": get_rating_options(params)
        }),
        ("contract_type", {
            "type": "radio",
            "label": _("Type"),
            "options": get_contract_type_options(params.get('contract_type'))
        }),
        ("shipping", {
            "type": "dropdown",
            "label": _("Ships to"),
            "options": get_region_options(params.get('shipping', default='any'))
        }),
        ("free_shipping_region", {
            "type": "checkbox",
            "label": _("Ships Free"),
            "options": get_free_shipping_options(
                params.get('free_shipping_region'),
                params.get('region', 'any')
            )
        }),
        ("connection", {
            "type": "radio",
            "label": _("Connection Type (Alpha)"),
            "options": get_connection_options(params.get('connection'))
        }),
        ("network", {
            "type": "radio",
            "label": _("Network"),
            "options": get_network_options(params.get('network'))
        }),
        ("dust", {
            "type": "checkbox",
            "label": _("Show Dust"),
            "options": get_dust_options(params)
        }),
        ("clear_all", {
            "type": "checkbox",
            "label": _("Reset"),
            "options": get_clear_all_options()
        }),
    ]

    if settings.DEV:
        from .dev import get_debug_options
        available_options += get_debug_options(params)

    options = OrderedDict(available_options)

    return options


def get_moderator_verified_options(p):
    moderator_verified = try_true_or_none(p)
    moderator_verified_choices = dict([(True, 'OB1 Verified Moderator'), ])
    return build_options(moderator_verified, moderator_verified_choices)


def get_moderator_options(p):
    moderator_count = try_int_or_zero(p)
    moderator_options = [
        {
            "value": v,
            "label": '\u2696' * v + ' ' + str(v) + '+',
            "checked": v == moderator_count,
            "default": False
        } for v in range(3, -1, -1)
    ]
    moderator_options[1]['default'] = True

    return moderator_options




def get_region_options(p):
    distinct_region = OrderedDict(
        country_list
    )
    return build_options(p, distinct_region)


def get_free_shipping_options(free, region):
    try:
        free_shipping = try_true_or_none(free)
    except MultiValueDictKeyError:
        free_shipping = ''
    if region and region.lower() != 'any':
        to_str = _('to {place}').format(place=region.title().replace('_', ' '))
        free_shipping_choices = OrderedDict([(True, to_str), ])
    else:
        free_shipping_choices = OrderedDict([(True, _('to Anywhere')), ])
    return build_options(free_shipping, free_shipping_choices)


def get_contract_type_options(p):
    contract = try_int_or_blank(p)
    return build_options(contract, Listing.CONTRACT_TYPE_DICT)


def get_condition_type_options(p):
    condition = try_int_or_blank(p)
    return build_options(condition, Listing.CONDITION_TYPE_DICT)


def get_rating_options(params):
    rating = try_param_or_zero(params.get('rating'), float)
    return [
        {
            "value": v,
            "label": "{:.2f}".format(v) + ' >=',
            "checked": v == rating,
            "default": False
        } for v in [5.0, 4.95, 4.8, 4.5, 4.0, 0.0]
    ]


def get_connection_options(p):
    connection = try_int_or_blank(p)
    return build_options(connection, Profile.CONNECTION_TYPE_DICT)


def get_dust_options(params):
    try:
        dust = True if params.get('dust') == 'true' else False
    except (ValueError, KeyError):
        dust = ''
    dust_str = _('> ~{p}% Bitcoin Fee').format(p=settings.DUST_FEE_PERCENT)
    dust_choices = OrderedDict([(True, dust_str), ])
    return build_options(dust, dust_choices)
