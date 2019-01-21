import operator
from functools import reduce

from django.db import models
from django.db.models.constants import LOOKUP_SEP
from django.template import loader
from django.utils import six
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from rest_framework.filters import BaseFilterBackend
from rest_framework.settings import api_settings
from rest_framework.compat import coreapi, coreschema, distinct
import django_filters
from django_filters.widgets import BooleanWidget
from distutils.util import strtobool
from ob.models import Listing, Profile

from django.db.models.fields import FieldDoesNotExist
from rest_framework.filters import OrderingFilter
from django.db.models.fields.reverse_related import ForeignObjectRel, OneToOneRel
from .widgets import TruthyWidget, FalsyWidget


class RelatedOrderingFilter(OrderingFilter):
    """

    See: https://github.com/tomchristie/django-rest-framework/issues/1005

    Extends OrderingFilter to support ordering by fields in related models
    using the Django ORM __ notation
    """

    def is_valid_field(self, model, field):
        """
        Return true if the field exists within the model (or in the related
        model specified using the Django ORM __ notation)
        """
        components = field.split('__', 1)
        try:
            field = model._meta.get_field(components[0])

            if isinstance(field, OneToOneRel):
                return self.is_valid_field(field.related_model, components[1])

            # reverse relation
            if isinstance(field, ForeignObjectRel):
                return self.is_valid_field(field.model, components[1])

            # foreign key
            if field.remote_field and len(components) == 2:
                return self.is_valid_field(field.related_model, components[1])
            return True
        except FieldDoesNotExist:
            return False

    def remove_invalid_fields(self, queryset, fields, ordering, view):
        return [term for term in fields
                if self.is_valid_field(queryset.model, term.lstrip('-'))]


class CustomSearchFilter(BaseFilterBackend):
    # The URL query parameter used for the search.
    search_param = api_settings.SEARCH_PARAM
    template = 'rest_framework/filters/search.html'
    lookup_prefixes = {
        '^': 'istartswith',
        '=': 'iexact',
        '@': 'search',
        '*': '',
        '$': 'iregex',
    }
    search_title = _('Search')
    search_description = _('A search term.')

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, '')
        if '*' == params:
            params = ''
        return params.replace(',', ' ').split()

    def construct_search(self, field_name):

        lookup = self.lookup_prefixes.get(field_name[0])
        if lookup:
            field_name = field_name[1:]
        else:
            lookup = 'icontains'
        return LOOKUP_SEP.join([field_name, lookup])

    def must_call_distinct(self, queryset, search_fields):
        """
        Return True if 'distinct()' should be used to query the given lookups.
        """
        for search_field in search_fields:
            opts = queryset.model._meta
            if search_field[0] in self.lookup_prefixes:
                search_field = search_field[1:]
            parts = search_field.split(LOOKUP_SEP)
            for part in parts:
                field = opts.get_field(part)
                if hasattr(field, 'get_path_info'):
                    # This field is a relation, update opts to follow the relation
                    path_info = field.get_path_info()
                    opts = path_info[-1].to_opts
                    if any(path.m2m for path in path_info):
                        # This field is a m2m relation so we know we need to call distinct
                        return True
        return False

    def filter_queryset(self, request, queryset, view):

        search_fields = getattr(view, 'search_fields', None)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(six.text_type(search_field))
            for search_field in search_fields
        ]

        base = queryset
        conditions = []
        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            conditions.append(reduce(operator.or_, queries))
        queryset = queryset.filter(reduce(operator.and_, conditions))

        if self.must_call_distinct(queryset, search_fields):
            # Filtering against a many-to-many field requires us to
            # call queryset.distinct() in order to avoid duplicate items
            # in the resulting queryset.
            # We try to avoid this if possible, for performance reasons.
            queryset = distinct(queryset, base)
        return queryset

    def to_html(self, request, queryset, view):
        if not getattr(view, 'search_fields', None):
            return ''

        term = self.get_search_terms(request)
        term = term[0] if term else ''
        context = {
            'param': self.search_param,
            'term': term
        }
        template = loader.get_template(self.template)
        return template.render(context)

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name=self.search_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text(self.search_title),
                    description=force_text(self.search_description)
                )
            )
        ]


class ProfileFilter(django_filters.FilterSet):
    # acceptedCurrencies = django_filters.Filter(field_name='moderator_accepted_currencies', lookup_expr='icontains')
    rating = django_filters.Filter(field_name='rating_average', lookup_expr='gte')
    version = django_filters.Filter(field_name='user_agent', lookup_expr='icontains')
    moderator_languages = django_filters.Filter(field_name='moderator_languages', lookup_expr='contains')
    has_email = django_filters.Filter(field_name='email', lookup_expr='isnull', exclude=True, widget=BooleanWidget())
    has_website = django_filters.Filter(field_name='website', lookup_expr='isnull', exclude=True,
                                        widget=BooleanWidget())
    is_moderator = django_filters.BooleanFilter(field_name='moderator', lookup_expr='exact', widget=BooleanWidget())
    is_verified = django_filters.Filter(field_name='verified', exclude=False, widget=TruthyWidget())
    has_verified = django_filters.Filter(field_name='listing__moderators__verified', widget=TruthyWidget())
    moderator_count = django_filters.NumberFilter(method='filter_listing_by_moderator_count')
    connection = django_filters.TypedChoiceFilter(field_name='connection_type',
                                                  choices=Profile.CONNECTION_TYPE_CHOICES)
    online = django_filters.Filter(field_name='online', widget=TruthyWidget())

    class Meta:
        model = Profile
        exclude = ()
        order_by = True

    def filter_listing_by_moderator_count(self, queryset, name, value):
        return queryset.filter(moderators_count__gte=value)


class ListingFilter(django_filters.FilterSet):
    acceptedCurrencies = django_filters.Filter(field_name='accepted_currencies', lookup_expr='icontains')
    tags = django_filters.Filter(field_name='tags', lookup_expr='icontains')
    categories = django_filters.Filter(field_name='categories', lookup_expr='icontains')
    rating = django_filters.Filter(field_name='rating_average', lookup_expr='gte')
    connection = django_filters.TypedChoiceFilter(field_name='profile__connection_type',
                                                  choices=Profile.CONNECTION_TYPE_CHOICES)
    condition_type = django_filters.ChoiceFilter(choices=Listing.CONDITION_TYPE_CHOICES)
    contract_type = django_filters.NumberFilter(field_name='contract_type', lookup_expr='icontains')
    moderator_count = django_filters.NumberFilter(method='filter_listing_by_moderator_count')
    moderator_verified = django_filters.Filter(field_name='moderators__verified', widget=TruthyWidget())
    online = django_filters.Filter(field_name='profile__online', widget=TruthyWidget())

    class Meta:
        model = Listing
        exclude = ()
        order_by = True

    def filter_listing_contract_type(self, queryset, name, value):
        return queryset.filter(contract_type=value)

    def filter_listing_by_moderator_count(self, queryset, name, value):
        return queryset.filter(moderators_count__gte=value)
