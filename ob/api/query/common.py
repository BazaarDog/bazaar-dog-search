from django.utils.timezone import now
from datetime import timedelta
from requests.exceptions import ConnectTimeout
from ob.models import Profile


def try_sync_peer(search_term):
    try:
        p = Profile.objects.get(pk=search_term)
        if now() - timedelta(hours=1) >= p.modified:
            try:
                p.sync()
            except ConnectTimeout:
                pass
        else:
            pass
    except Profile.DoesNotExist:
        p = Profile(pk=search_term)
        try:
            p.sync()
        except ConnectTimeout:
            pass
