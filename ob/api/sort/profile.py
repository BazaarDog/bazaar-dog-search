from collections import OrderedDict
from django.utils.translation import ugettext_lazy as _


def get_profile_sort():
    return OrderedDict([
        ("", {
            "label": _("Relevance"),
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