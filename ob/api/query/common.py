from datetime import timedelta
from requests.exceptions import ConnectTimeout

from django.utils.timezone import now

from ob.models.profile import Profile
from ob.tasks.sync_profile import sync_profile
from ob.tasks.sync_listing import sync_listing


def check_peer(query_params):
    if 'q' in query_params:
        search_term = query_params['q']
        if 'Qm' == search_term[:2] and len(search_term) >= 40:
            try_sync_peer(search_term)


def try_sync_peer(search_term):
    try:
        profile = Profile.objects.get(pk=search_term)
        if now() - timedelta(minutes=3) >= profile.modified:
            do_sync_peer(profile)
        else:
            pass
    except Profile.DoesNotExist:
        profile, created = Profile.objects.get_or_create(pk=search_term)
        do_sync_peer(profile)


def do_sync_peer(profile):
    try:
        sync_profile(profile)
        for l in profile.listing_set.all():
            sync_listing(l)
    except ConnectTimeout:
        pass


def get_nsfw_filter_queryset(queryset, nsfw):

    if nsfw == 'Affirmative':
        return queryset.filter(nsfw=True)
    elif nsfw == 'true' or nsfw is True:
        return queryset
    else:
        return queryset.exclude(nsfw=True)
