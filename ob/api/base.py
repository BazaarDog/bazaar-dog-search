from django.conf import settings
from django.core.paginator import InvalidPage
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import six
from django.utils.translation import ugettext_lazy, ugettext

from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from ob.api.sort.listing import get_sort
from .param.listing import get_listing_options
from .param.profile import get_profile_options
from .sort.profile import get_profile_sort


class ListingResultsSetPagination(PageNumberPagination):
    page_size = 24
    page_query_param = 'p'
    page_size_query_param = 'ps'
    max_page_size = 480

    def get_paginated_response(self, data):

        options = get_options(self.request.query_params)
        sort_by = get_sort()
        if 'clear_all' in self.request.query_params.keys():
            if self.request.query_params['clear_all'] == 'true':
                return redirect(settings.SITE_URL)

        if 'locale' in self.request.query_params.keys():
            from django.utils import translation
            translation.activate(self.request.query_params['locale'])
            self.request.LANGUAGE_CODE = translation.get_language()

        q = (self.request.query_params['q'] if 'q' in self.request.query_params.keys() else '')

        if settings.ONION:
            endpoint_name = ugettext_lazy("𝕭𝖆𝖟𝖆𝖆𝖗 𝕯𝖔𝖌")
        else:
            endpoint_name = ugettext_lazy("Bazaar Dog")

        return Response({'name': endpoint_name,
                         "logo": settings.SITE_URL + "/logo.png",
                         "q": q,
                         "links": {
                             "self": settings.SITE_URL + "/api/",
                             "search": settings.SITE_URL + "/api/",
                             "reports": settings.SITE_URL + reverse('api-public:report-listing'),
                             "listings": settings.SITE_URL + "/api/"
                         },
                         "results": {
                             'morePages': self.get_has_more(),
                             'results': data,
                             'total': self.page.paginator.count,
                         },
                         'options': options,
                         'sortBy': sort_by,
                         })

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """

        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        page_number = str(int(page_number) + 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)

        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_has_more(self):
        if not self.page.has_next():
            return False
        else:
            return True


class ListingPaginateAPIView(generics.ListAPIView):
    pagination_class = ListingResultsSetPagination


class ProfileResultsSetPagination(PageNumberPagination):
    page_size = 24
    page_query_param = 'p'
    page_size_query_param = 'ps'
    max_page_size = 480

    def get_paginated_response(self, data):

        options = get_profile_options(self.request.query_params)
        sort_by = get_profile_sort()

        if 'clear_all' in self.request.query_params.keys():
            if self.request.query_params['clear_all'] == 'true':
                return redirect(settings.SITE_URL + "/profile/")
        if 'locale' in self.request.query_params.keys():
            from django.utils import translation
            translation.activate(self.request.query_params['locale'])
            self.request.LANGUAGE_CODE = translation.get_language()

        q = (self.request.query_params['q'] if 'q' in self.request.query_params.keys() else '')

        if settings.ONION:
            endpoint_name = ugettext("𝕭𝖆𝖟𝖆𝖆𝖗 𝕯𝖔𝖌") + " { " + ugettext("𝔓𝔯𝔬𝔣𝔦𝔩𝔢𝔰") + " }"
        else:
            endpoint_name = ugettext("Bazaar Dog") + " ( " + ugettext("Profiles") + " )"  # + " " + get_language()

        return Response({'name': endpoint_name,
                         "logo": settings.SITE_URL + "/logo_profile.png",
                         "q": q,
                         "links": {
                             "self": settings.SITE_URL + "/profile/",
                             "search": settings.SITE_URL + "/profile/",
                             "reports": settings.SITE_URL + reverse('api-public:report-listing'),
                             "listings": settings.SITE_URL + "/profile/"
                         },
                         "results": {
                             'morePages': self.get_has_more(),
                             'results': data,
                             'total': self.page.paginator.count,
                         },
                         'options': options,
                         'sortBy': sort_by,
                         })

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """

        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        page_number = str(int(page_number) + 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)

        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_has_more(self):
        if not self.page.has_next():
            return False
        else:
            return True


class ProfilePaginateAPIView(generics.ListAPIView):
    pagination_class = ProfileResultsSetPagination
