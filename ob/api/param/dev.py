from collections import OrderedDict
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from .util import build_options


def get_debug_options(params):

    locale = params.get('locale')
    translation_languages = OrderedDict(
        [('', _('Default'))] + settings.LANGUAGES)
    translation_languages_options = build_options(locale, translation_languages)

    if params.get('online'):
        online_raw = params.get('online')
        if online_raw == 'true':
            online = True
        else:
            online = False
    else:
        online = ''

    online_choices = OrderedDict(
        [
            (True, _('Online')),
            ('', _('All')),
        ]
    )
    online_options = build_options(online, online_choices)

    debug_options = [
        (
            "locale", {
                "type": "dropdown",
                "label": _("Language"),
                "options": translation_languages_options
            },
        ),
        (
            "online", {
                "type": "radio",
                "label": _("Online"),
                "options": online_options
            }
        ),
    ]

    return debug_options
