from .base import *
from .serializer import *
from .filter import *
from django.db.models import Q, Prefetch
from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import filters
from django.db.models import Prefetch, Count, Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import now
from datetime import timedelta
from requests.exceptions import ConnectTimeout
from ob.models import Listing, ListingReport

class Report(generics.CreateAPIView):

    model = ListingReport
    serializer_class = ListingReportSerializer

class ProfileSearch(ProfilePaginateAPIView):

    model = Profile
    serializer_class = ProfileWrapSerializer
    ordering = Profile._meta.ordering
    filter_class = ProfileFilter

    filter_backends = (DjangoFilterBackend,filters.OrderingFilter,CustomSearchFilter,)
    ordering_fields = ('__all__')
    search_fields = ('name','about','short_description','peerID',)

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
        ).filter(Q(vendor=True) | Q(moderator=True)).exclude(name='')\
            .exclude(scam=True) \
            .filter(was_online__gt=a_week_ago)\
            .exclude(illegal_in_us=True)

        if 'acceptedCurrencies' in self.request.query_params:
            c = self.request.query_params['acceptedCurrencies']
            queryset = queryset.filter( Q(moderator_accepted_currencies__icontains=c) | Q(listing__accepted_currencies__icontains=c))
        queryset = queryset.annotate(moderators_count=Count('listing__moderators', distinct=True))

        if 'q' in self.request.query_params:
            search_term = self.request.query_params['q']
            if 'Qm' == search_term[:2] and len(search_term) >= 40:
                try:
                    p = Profile.objects.get(pk=search_term)
                    if now() - timedelta(hours=1) >= p.modified:
                        #print('SYNC BY SEARCH ' + search_term)
                        try:
                            if 'network' in self.request.query_params:
                                is_testnet = (True if self.request.query_params['network'] == 'testnet' else False)
                            else:
                                is_testnet = False
                            p.sync(is_testnet)
                        except ConnectTimeout:
                            pass
                    else:
                        pass
                        #print('not syncing ' + search_term)
                except Profile.DoesNotExist:
                    p = Profile(pk=search_term)
                    try:
                        p.sync()
                    except ConnectTimeout:
                        pass

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


class ListingSearch(ListingPaginateAPIView):

    model = Listing
    serializer_class = ListingWrapSerializer
    ordering = Listing._meta.ordering

    filter_class = ListingFilter

    filter_backends = (DjangoFilterBackend,filters.OrderingFilter,CustomSearchFilter,RelatedOrderingFilter,)
    ordering_fields = ('__all__')
    search_fields = ('description','tags','categories','title','profile__peerID','profile__handle','profile__name',)


    def get_queryset(self):

        if 'q' in self.request.query_params:
            search_term = self.request.query_params['q']
            if 'Qm' == search_term[:2] and len(search_term) >= 40:
                try:
                    p = Profile.objects.get(pk=search_term)
                    if now() - timedelta(hours=1) >= p.modified:
                        #print('SYNC BY SEARCH ' + search_term)
                        try:
                            if 'network' in self.request.query_params:
                                is_testnet = (True if self.request.query_params['network'] == 'testnet' else False)
                            else:
                                is_testnet = False
                            p.sync(is_testnet)
                        except ConnectTimeout:
                            pass
                    else:
                        pass
                        #print('not syncing ' + search_term)
                except Profile.DoesNotExist:
                    p = Profile(pk=search_term)
                    try:
                        p.sync()
                    except ConnectTimeout:
                        pass

        if 'dust' in self.request.query_params and self.request.query_params['dust'] == 'true':
            dust_param = [True,False]
        else:
            dust_param = [False]

        a_week_ago = now() - timedelta(hours=156)
        queryset = Listing.objects \
            .prefetch_related(
            "moderators",
            Prefetch(
                    "images",
                    queryset=ListingImage.objects.filter(index=0),
                    to_attr="thumbnail"),
            Prefetch(
                "profile__avatar",
                queryset=Image.objects.filter(),
                to_attr="avatar_prefetch")
            ) \
            .select_related('profile') \
            .filter(profile__vendor=True) \
            .filter(profile__was_online__gt=a_week_ago) \
            .exclude(pricing_currency__isnull=True) \
            .exclude(pricing_currency__exact='') \
            .exclude(profile__scam=True) \
            .filter(dust__in=dust_param) \
            .exclude(profile__illegal_in_us=True)
            #.filter(active=True) \ this is redundant with vendor=True

        queryset = queryset.annotate(moderators_count=Count('moderators'))

        if 'shipping' in self.request.query_params:
            c = self.request.query_params['shipping']
            queryset = queryset.filter(Q(shippingoptions__regions__icontains=c) | Q(shippingoptions__regions__icontains='ALL')| Q(shippingoptions__regions__isnull=True))

        if 'free_shipping_region' in self.request.query_params and self.request.query_params['free_shipping_region'] == 'true':
            if self.request.query_params['shipping']:
                c = self.request.query_params['shipping']
            else:
                c = 'ALL'
            queryset = queryset.filter(contract_type=Listing.PHYSICAL_GOOD).filter(Q(free_shipping__icontains=c) | Q(free_shipping__icontains='ALL') | Q(shippingoptions__regions__isnull=True))


        if 'nsfw' in self.request.query_params:
            value = self.request.query_params['nsfw']
            #print('get_query nsfw value is ' + str(value))
            if not value:
                return queryset.exclude(nsfw=True)
            elif value == 'Affirmative':
                return queryset.filter(nsfw=True)
            elif value == 'true' or value == True:
                return queryset
            else:
                return queryset.exclude(nsfw=True)
        else:
            return queryset.exclude(nsfw=True)