from ob.api.serializer import *
from django.db.models import Q, Prefetch, Count
from django.utils.timezone import now
from datetime import timedelta
from ob.models.profile import Profile
from .common import check_peer


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

    currencies = self.request.query_params.get('acceptedCurrencies')
    if currencies:
        queryset = queryset.filter(
            Q(moderator_accepted_currencies__icontains=currencies) |
            Q(listing__accepted_currencies__icontains=currencies))

    queryset = queryset.annotate(
        moderators_count=Count('listing__moderators', distinct=True))

    check_peer(self.request.query_params)

    nsfw = self.request.query_params['nsfw']
    if not nsfw:
        return queryset.exclude(nsfw=True)
    elif nsfw == 'Affirmative':
        return queryset.filter(nsfw=True)
    elif nsfw == 'true' or nsfw is True:
        return queryset
    else:
        return queryset.exclude(nsfw=True)

    return queryset

