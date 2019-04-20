from datetime import timedelta
from requests.exceptions import ConnectTimeout

from django.utils.timezone import now

from ob.models.profile import Profile
from ob.tasks.sync_profile import sync_profile


def check_peer(query_params):
    if 'q' in query_params:
        search_term = query_params['q']
        if 'Qm' == search_term[:2] and len(search_term) >= 40:
            try_sync_peer(search_term)


def try_sync_peer(search_term):
    try:
        profile = Profile.objects.get(pk=search_term)
        if now() - timedelta(hours=1) >= profile.modified:
            try:
                sync_profile(profile)
            except ConnectTimeout:
                pass
        else:
            pass
    except Profile.DoesNotExist:
        profile = Profile(pk=search_term)
        try:
            sync_profile(profile)
        except ConnectTimeout:
            pass
