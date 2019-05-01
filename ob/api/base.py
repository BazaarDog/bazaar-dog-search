from django.conf import settings
from django.core.paginator import InvalidPage
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import six
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext

from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from ob.api.param.listing import get_listing_options
from ob.api.param.profile import get_profile_options
from ob.api.sort.listing import get_sort
from ob.api.sort.profile import get_profile_sort


def get_endpoint_name(is_profile=False):
    names = {
        # Is Onion
        True:
            {
                True: ugettext("𝕭𝖆𝖟𝖆𝖆𝖗 𝕯𝖔𝖌") + " {" + ugettext(
                    "𝔓𝔯𝔬𝔣𝔦𝔩𝔢𝔰") + "}",
                False: ugettext("𝕭𝖆𝖟𝖆𝖆𝖗 𝕯𝖔𝖌")
            },
        # Is Clearnet
        False:
            {
                True: ugettext("Bazaar Dog") + " (" + ugettext(
                    "Profiles") + ")",
                False: ugettext("Bazaar Dog")
            },
    }
    return names[settings.ONION][is_profile]


def get_translation(locale):
    from django.utils import translation
    translation.activate(locale)
    return translation.get_language()


class CustomPaginateMixin(PageNumberPagination):
    page_size = 24
    page_query_param = 'p'
    page_size_query_param = 'ps'
    max_page_size = 480

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """

        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 0)
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

    def get_response(self, endpoint, q, data, options, sort_by):
        return Response({'name': endpoint.get('endpoint_name'),
                         "logo": endpoint.get('logo_url'),
                         "q": q,
                         "links": {
                             "self": endpoint.get('endpoint_url'),
                             "search": endpoint.get('endpoint_url'),
                             "reports": endpoint.get('report_url'),
                             "listings": endpoint.get('endpoint_url')
                         },
                         "results": {
                             'morePages': self.get_has_more(),
                             'results': data,
                             'total': self.page.paginator.count,
                         },
                         'options': options,
                         'sortBy': sort_by,
                         })


class ListingResultsSetPagination(CustomPaginateMixin):
    def get_paginated_response(self, data):

        q = self.request.query_params.get('q')
        options = get_listing_options(self.request.query_params)
        sort_by = get_sort()
        if self.request.query_params.get('clear_all') == 'true':
            return redirect(settings.SITE_URL, query_string=False)

        locale = self.request.query_params.get('locale')
        if locale:
            self.request.LANGUAGE_CODE = get_translation(locale)

        endpoint = {}
        site = settings.SITE_URL
        endpoint['endpoint_name'] = get_endpoint_name()
        endpoint['endpoint_url'] = site + reverse('api-public:listing-page')
        endpoint['logo_url'] = site + reverse('logo')
        endpoint['report_url'] = site + reverse('api-public:report-listing')
        return self.get_response(endpoint, q, data, options, sort_by)


class ListingPaginateAPIView(generics.ListAPIView):
    pagination_class = ListingResultsSetPagination


class ProfileResultsSetPagination(CustomPaginateMixin):
    def get_paginated_response(self, data):

        if self.request.query_params.get('clear_all') == 'true':
            return redirect(reverse('api-public:profile-page'),
                            query_string=False)

        options = get_profile_options(self.request.query_params)
        sort_by = get_profile_sort()
        q = self.request.query_params.get('q')
        locale = self.request.query_params.get('locale')
        if locale:
            self.request.LANGUAGE_CODE = get_translation(locale)

        endpoint = {}
        site = settings.SITE_URL
        endpoint['endpoint_name'] = get_endpoint_name(is_profile=True)
        endpoint['endpoint_url'] = site + reverse('api-public:profile-page')
        endpoint['logo_url'] = site + reverse('profile-logo')
        endpoint['report_url'] = site + reverse('api-public:report-listing')
        return self.get_response(endpoint, q, data, options, sort_by)


class ProfilePaginateAPIView(generics.ListAPIView):
    pagination_class = ProfileResultsSetPagination
