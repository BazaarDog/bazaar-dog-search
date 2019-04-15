from distutils.util import strtobool
from collections import OrderedDict
import logging
from ob.models import Profile
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from .util import build_options, build_checkbox
from .common import get_nsfw_options, get_currency_type_options, get_clear_all_options, get_network_options

logger = logging.getLogger(__name__)

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

    available_options = [
        ("acceptedCurrencies", {
            "type": "radio",
            "label": _("Accepted Currencies"),
            "options": get_currency_type_options(params)
        }),
        ("is_verified", {
            "type": "checkbox",
            "label": _("Verification"),
            "options": get_is_verified_options(params)
        }),
        ("is_moderator", {
            "type": "radio",
            "label": _("Offers Moderation"),
            "options": get_is_moderator_options(params)
        }),
        ("moderator_languages", {
            "type": "dropdown",
            "label": _("Moderator Language"),
            "options": get_moderator_languages_options(params)
        }),
        ("has_verified", {
            "type": "checkbox",
            "label": _("Store Verification"),
            "options": get_has_verified_options(params)
        }),
        ("moderator_count", {
            "type": "radio",
            "label": _("Store Moderators Available"),
            "options": get_has_moderator_options(params)
        }),
        ("rating", {
            "type": "radio",
            "label": _("Vendor Rating"),
            "options": get_rating_options(params)
        }),
        ("version", {
            "type": "radio",
            "label": _("Server Version"),
            "options": get_ua_options(params)
        }),
        ("nsfw", {
            "type": "radio",
            "label": _("Adult Content"),
            "options": get_nsfw_options(params)
        }),
        ("connection", {
            "type": "radio",
            "label": _("Connection Type"),
            "options": get_connection_options(params)
        }),
        ("network", {
            "type": "radio",
            "label": _("Network"),
            "options": get_network_options(params)
        }),
        ("clear_all", {
            "type": "checkbox",
            "label": _("Reset"),
            "options": get_clear_all_options()
        }),
    ]
    if settings.DEV:
        from ob.api.param.dev import get_debug_options
        available_options += get_debug_options(params)

    options = OrderedDict(available_options)

    return options


def get_ua_options(params):

    version = params.get('version')

    distinct_version = OrderedDict(
        [
            ('openbazaar-go:0.14', '0.14.*'),
            ('openbazaar-go:0.13', '0.13.*'),
            ('openbazaar-go:0.12', '0.12.*'),
            ('openbazaar-go:0.11', '0.11.*'),
            ('openbazaar-go:0.10', '0.10.*'),
            ('openbazaar-go:0.9', '0.9.*'),
            ('', 'Any')
        ]
    )

    return build_options(version, distinct_version)


def get_has_moderator_options(params):

    if 'moderator_count' in params.keys():
        try:
            moderator_count = int(params['moderator_count'])
        except ValueError:
            moderator_count = 0
    else:
        moderator_count = 0

    return [
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


def get_is_moderator_options(params):

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

    return build_options(is_moderator, is_moderator_choices)


def get_is_verified_options(params):

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
                # logger.debug('moderator found:' + str(is_moderator))
        except ValueError:
            is_verified = ''
    else:
        is_verified = ''

    is_verified_choices = OrderedDict(
        [(True, _('Is an OB1 Verified Moderator')), ])

    return build_options(is_verified, is_verified_choices)


def get_has_verified_options(params):

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
                # logger.debug('moderator found:' + str(is_moderator))
        except ValueError:
            has_verified = ''
    else:
        has_verified = ''

    has_verified_choices = OrderedDict([(True, _('Has OB1 Verified Moderator')), ])

    return build_options(has_verified, has_verified_choices)


def get_moderator_languages_options(params):

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

    return build_options(lang, moderator_languages)


def get_rating_options(params):

    try:
        rating = float(params['rating'])
    except ValueError:
        rating = 0
    except KeyError:
        rating = 0

    return [
        {
            "value": v,
            "label": "{:.2f}".format(v) + ' >=',
            "checked": v == rating,
            "default": False
        } for v in [5.0, 4.95, 4.9, 4.8, 4.5, 4.0, 0.0]
    ]


def get_connection_options(params):

    try:
        connection = int(params['connection'])
    except ValueError:
        connection = ''
    except KeyError:
        connection = ''

    return build_options(connection, Profile.CONNECTION_TYPE_DICT)

