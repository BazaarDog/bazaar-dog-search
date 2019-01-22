from collections import OrderedDict
from django.utils.translation import ugettext_lazy as _


def get_sort():
    return OrderedDict([
        ("", {
            "label": _("Relevance"),
            "selected": False,
            "default": True
        }),
        ("price_value", {
            "label": _("Price (Low to High)"),
            "selected": False,
            "default": False
        }),
        ("-price_value", {
            "label": _("Price (High to Low)"),
            "selected": False,
            "default": False
        }),
        ("-rating_dot", {
            "label": _("Rating"),
            "selected": False,
            "default": False
        }),
        ("signature", {
           "label": _("Random"),
           "selected": False,
           "default": False
        }),
        #("profile__speed_rank", {
        #    "label": _("Fastest"),
        #    "selected": False,
        #    "default": False
        #}),
        ("-created", {
            "label": _("Newest"),
            "selected": False,
            "default": False
        }),
        ("created", {
            "label": _("Oldest"),
            "selected": False,
            "default": False
        }),
        ("title", {
            "label": _("Title A-Z"),
            "selected": False,
            "default": False
        }),
        ("-title", {
            "label": _("Title Z-A"),
            "selected": False,
            "default": False
        }),
        ("rank", {
            "label": _("Least Relevant️"),
            "selected": False,
            "default": False
        }),
    ])