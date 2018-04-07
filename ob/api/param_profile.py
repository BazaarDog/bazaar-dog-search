from distutils.util import strtobool
from collections import OrderedDict
from ob.models import Listing, Profile
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from .param_util import build_options, build_checkbox


def get_profile_sort():
    return OrderedDict([
        ("", {
            "label": _("Relevance"),
            "selected": False,
            "selected": False,
            "default": True
        }),
        ("-listing_count", {
            "label": _("Items Listed (High to Low)"),
            "selected": False,
            "default": False
        }),
        ("-moderated_items_count", {
            "label": _("Moderating (High to Low)"),
            "selected": False,
            "default": False
        }),
        ("-rating_dot", {
            "label": _("Rating"),
            "selected": False,
            "default": False
        }),
    ])


def get_profile_options(params):
    clear_all_options = [
        {"value": True,
         "label": _("Reset"),
         "checked": False,
         "default": False
         }
    ]

    if 'acceptedCurrencies' in params.keys():
        currency = params['acceptedCurrencies']
    else:
        currency = ''

    distinct_currency = OrderedDict(
        [
            ('BCH', _('Bitcoin Cash') + ' (BCH)'),
            ('BTC', _('Bitcoin Legacy') + ' (BTC)'),
            # ('DOGE', 'Dogecoin (DOGE)'),
            # ('ETH', 'Ethereum (ETH)'),
            # ('ETC', 'Ethereum Classic (ETC)'),
            # ('LTC', 'Litecoin (LTC)'),
            ('ZEC', 'ZCash (ZEC)'),
            #('XZC', 'ZCoin (XZC)'),
            ('ZEN', 'ZenCash (ZEN)'),
            ('', _('Any'))
        ]
    )

    currency_type_options = build_options(currency, distinct_currency)

    if 'version' in params.keys():
        version = params['version']
        # print('version found:' + version)
    else:
        version = ''

    distinct_version = OrderedDict(
        [
            ('openbazaar-go:0.11', '0.11.*'),
            ('openbazaar-go:0.10', '0.10.*'),
            ('openbazaar-go:0.9', '0.9.*'),
            ('', 'Any')
        ]
    )

    ua_options = build_options(version, distinct_version)

    if 'moderator_count' in params.keys():
        try:
            moderator_count = int(params['moderator_count'])
        except ValueError:
            moderator_count = 0
    else:
        moderator_count = 0

    has_moderator_options = [
        {
            "value": v,
            "label": '\u2696️' * v + ' ' + str(v) + '+',
            "checked": True,
            "default": False
        }
        if v == moderator_count else
        {
            "value": v,
            "label": '\u2696' * v + ' ' + str(v) + '+',
            "checked": False, "default": False
        } for v in range(3, -1, -1)
    ]

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
                # print('nsfw found:' + str(nsfw))
        except ValueError:
            nsfw = False
    else:
        nsfw = False

    nsfw_choicea = OrderedDict(
        [
            (False, _('Hide')),
            (True, _('Show')),
            ('Affirmative', _('Only NSFW'))
        ]
    )

    nsfw_options = build_options(nsfw, nsfw_choicea)

    if 'is_moderator' in params.keys():
        try:
            if params['is_moderator'] == 'true':
                is_moderator = True
            elif params['is_moderator'] == 'false':
                is_moderator = ''
            elif params['is_moderator'] == '':
                is_moderator = ''
            else:
                is_moderator = ''
        except ValueError:
            is_moderator = ''
    else:
        is_moderator = ''

    is_moderator_choices = OrderedDict(
        [(True, _('Yes')), ('', _('All')), ])

    is_moderator_options = build_options(is_moderator, is_moderator_choices)

    if 'is_verified' in params.keys():
        try:
            if params['is_verified'] == 'true':
                is_verified = True
            elif params['is_verified'] == 'false':
                is_verified = ''
            elif params['is_verified'] == '':
                is_verified = ''
            else:
                is_verified = ''
                # print('moderator found:' + str(is_moderator))
        except ValueError:
            is_verified = ''
    else:
        is_verified = ''

    is_verified_choices = OrderedDict(
        [(True, _('Is an OB1 Verified Moderator')), ])

    is_verified_options = build_options(is_verified, is_verified_choices)

    if 'has_verified' in params.keys():
        try:
            if params['has_verified'] == 'true':
                has_verified = True
            elif params['has_verified'] == 'false':
                has_verified = ''
            elif params['has_verified'] == '':
                has_verified = ''
            else:
                has_verified = ''
                # print('moderator found:' + str(is_moderator))
        except ValueError:
            has_verified = ''
    else:
        has_verified = ''

    has_verified_choices = OrderedDict([(True, _('Has OB1 Verified Moderator')), ])

    has_verified_options = build_options(has_verified, has_verified_choices)

    if 'moderator_languages' in params.keys():
        lang = params['moderator_languages']
    else:
        lang = ''

    moderator_languages = OrderedDict([
        ("", "All"), ("zh", "中文"), ("es", "Español"), ("en", "English"), ("hi", "हिन्दी"), ("ar", "العربية"),
        ("pt", "português"), ("bg", "български"), ("ru", "русский"), ("ja", "日本語"), ("pa", "ਪੰਜਾਬੀ"),
        ("de", "Deutsch"), ("ko", "한국어"), ("fr", "français"), ("tr", "Türkçe"), ("it", "italiano"),
        ("pl", "polski"), ("ro", "română"), ("nl", "Nederlands"), ("da", "Dansk"), ("fi", "Suomi"), ("sv", "Svenska"),
        ("ta", "தமிழ்"), ("el", "Ελληνικά"), ("cs", "čeština"), ("eu", "Euskara"), ("hr", "Hrvatski"),
        ("mk", "македонски"), ("af", "Afrikaans")
    ])

    moderator_languages_options = build_options(lang, moderator_languages)

    if 'network' in params.keys():
        network = params['network']
        # print('network found:' + network)
    else:
        network = 'mainnet'

    network_choices = OrderedDict([('mainnet', _("Main Network")), ('testnet', _("Test Network")), ])

    network_options = build_options(network, network_choices)

    if 'rating' in params.keys():
        try:
            rating = float(params['rating'])
        except ValueError:
            rating = 0

    else:
        rating = 0

    rating_options = [
        {
            "value": v,
            "label": "{:.2f}".format(v) + ' >=',
            "checked": v == rating,
            "default": False
        } for v in [5.0, 4.95, 4.9, 4.8, 4.5, 4.0, 0.0]
    ]

    if 'connection' in params.keys():
        try:
            connection = int(params['connection'])
        except ValueError:
            connection = ''
            # print('connection found:' + str(connection) + " class" + str(type(connection)))
    else:
        connection = ''

    connection_options = build_options(connection, Profile.CONNECTION_TYPE_DICT)

    available_options = [
        ("acceptedCurrencies", {
            "type": "radio",
            "label": _("Accepted Currencies"),
            "options": currency_type_options
        }),
        ("is_verified", {
            "type": "checkbox",
            "label": _("Verification"),
            "options": is_verified_options
        }),
        ("is_moderator", {
            "type": "radio",
            "label": _("Offers Moderation"),
            "options": is_moderator_options
        }),
        ("moderator_languages", {
            "type": "dropdown",
            "label": _("Moderator Language"),
            "options": moderator_languages_options
        }),
        ("has_verified", {
            "type": "checkbox",
            "label": _("Store Verification"),
            "options": has_verified_options
        }),
        ("moderator_count", {
            "type": "radio",
            "label": _("Store Moderators Available"),
            "options": has_moderator_options
        }),
        ("rating", {
            "type": "radio",
            "label": _("Vendor Rating"),
            "options": rating_options
        }),
        ("version", {
            "type": "radio",
            "label": _("Server Version"),
            "options": ua_options
        }),
        ("nsfw", {
            "type": "radio",
            "label": _("Adult Content"),
            "options": nsfw_options
        }),
        ("connection", {
            "type": "radio",
            "label": _("Connection Type"),
            "options": connection_options
        }),
        ("network", {
            "type": "radio",
            "label": _("Network"),
            "options": network_options
        }),
        ("clear_all", {
            "type": "checkbox",
            "label": _("Reset"),
            "options": clear_all_options
        }),
    ]
    if settings.DEV:
        from .param_dev import get_debug_options
        available_options += get_debug_options(params)

    options = OrderedDict(available_options)

    return options
