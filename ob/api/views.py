from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from ob.api.query.profile import get_queryset as get_queryset_profile
from ob.models.listing_report import ListingReport
from ob.models.listing import Listing
from ob.models.profile import Profile
from .base import *
from .filter import *
from .query.listing import get_queryset as get_queryset_listing
from .serializer import ListingReportSerializer, ProfileWrapSerializer, \
    ListingWrapSerializer


class Report(generics.CreateAPIView):
    model = ListingReport
    serializer_class = ListingReportSerializer


class ProfileSearch(ProfilePaginateAPIView):
    model = Profile
    serializer_class = ProfileWrapSerializer
    ordering = Profile._meta.ordering
    filter_class = ProfileFilter

    filter_backends = (DjangoFilterBackend,
                       filters.OrderingFilter,
                       CustomSearchFilter,)
    ordering_fields = ('__all__')
    search_fields = ('name', 'about', 'short_description',
                     'peerID', 'moderator_accepted_currencies',)
    get_queryset = get_queryset_profile


class ListingSearch(ListingPaginateAPIView):
    model = Listing
    serializer_class = ListingWrapSerializer
    ordering = Listing._meta.ordering

    filter_class = ListingFilter

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,
                       CustomSearchFilter, RelatedOrderingFilter,)
    ordering_fields = ('__all__')
    search_fields = (
        'description', 'tags', 'categories',
        'title', 'profile__peerID', 'profile__handle', 'profile__name',)
    get_queryset = get_queryset_listing
