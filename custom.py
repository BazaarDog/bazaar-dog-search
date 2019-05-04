import math
from django.conf import settings

from random import randint


def get_listing_rank(self):
    return 1


def get_profile_rank(self):
    return 1


def mark_scammers():
    from ob.models.profile import Profile
    known_scammers = []
    return Profile.objects.filter(pk__in=known_scammers).update(scam=True)


def mark_dust():
    from ob.models.listing import Listing
    update_count = Listing.objects \
        .filter(price_value__lt=0.001,
                accepted_currencies__icontains='BTC')\
        .exclude(accepted_currencies__icontains='BCH')\
        .exclude(accepted_currencies__icontains='ETH')\
        .exclude(accepted_currencies__icontains='LTC')\
        .exclude(accepted_currencies__icontains='ZEC')\
        .update(dust=True)
    return update_count


good_nodes = [
    "QmVFNEj1rv2d3ZqSwhQZW2KT4zsext4cAMsTZRt5dAQqFJ",  # "Jacob Ian"
    "QmeRw4K4s5HvWmYZhTdDt8mdr5rf6MCNZHW51T8ZmKKF9g",  # "Max aka @Anyone"
    "QmRrwvM4bRSKSTsyy1K3jkjJow67H52n39iBuuaCi48EZn",  # "OB Lawyer"
    "QmeSyTRaNZMD8ajcfbhC8eYibWgnSZtSGUp3Vn59bCnPWC",  # "Matthew Zipkin"
    "QmcNqUgkrWpy4XfbjPYX7ZicU23LLLVP65Y5vpmr9epgyd",  # "SamPatt (OB1)"
    "QmcUDmZK8PsPYWw5FRHKNZFjszm2K6e68BQSTpnJYUsML7",  # "OpenBazaar Store"
]
