from ob.api.serializer import *
from django.db.models import Q, Prefetch, Count
from django.utils.timezone import now
from datetime import timedelta
from ob.models import Profile
from .common import try_sync_peer


def get_queryset(self):

    a_week_ago = now() - timedelta(hours=156)

    queryset = Profile.objects.filter().prefetch_related(Prefetch(
        "avatar",
        queryset=Image.objects.filter(),
        to_attr="avatar_prefetch")
    ).prefetch_related(Prefetch(
        "header",
        queryset=Image.objects.filter(),
        to_attr="header_prefetch")
    ).filter(Q(vendor=True) | Q(moderator=True)).exclude(name='') \
        .exclude(scam=True) \
        .filter(was_online__gt=a_week_ago) \
        .exclude(illegal_in_us=True)

    if 'acceptedCurrencies' in self.request.query_params:
        c = self.request.query_params['acceptedCurrencies']
        queryset = queryset.filter(
            Q(moderator_accepted_currencies__icontains=c) | Q(listing__accepted_currencies__icontains=c))
    queryset = queryset.annotate(moderators_count=Count('listing__moderators', distinct=True))

    if 'q' in self.request.query_params:
        search_term = self.request.query_params['q']
        if 'Qm' == search_term[:2] and len(search_term) >= 40:
            try_sync_peer(search_term)

    if 'nsfw' in self.request.query_params:
        value = self.request.query_params['nsfw']
        if not value:
            return queryset.exclude(nsfw=True)
        elif value == 'Affirmative':
            return queryset.filter(nsfw=True)
        elif value == 'true' or value is True:
            return queryset
        else:
            return queryset.exclude(nsfw=True)
    else:
        return queryset.exclude(nsfw=True)