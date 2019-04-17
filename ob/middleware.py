from django.shortcuts import redirect

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class HumanizeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # this redirects traffic not originating from ob to
        # a human readable website
        if not settings.DEV and not settings.DEBUG:
            ua = request.META.get('HTTP_USER_AGENT')
            if ua and "OpenBazaar" not in ua:
                return redirect('https://www.bazaar.dog/')


class ForceCORS(MiddlewareMixin):
    def process_response(self, request, response):
        response['Access-Control-Allow-Origin'] = "*"
        return response
