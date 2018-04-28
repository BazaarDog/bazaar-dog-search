from django.shortcuts import redirect

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class HumanizeMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if 'bazaar.dog' in request.META['HTTP_ORIGIN']:
            pass
        if 'localhost' in request.META['HTTP_ORIGIN']:
            pass
        elif not settings.DEV and not settings.DEBUG:

            try:
                if "OpenBazaar" not in request.META['HTTP_USER_AGENT']:
                    return redirect('https://www.bazaar.dog/')
            except KeyError:
                return redirect('https://www.bazaar.dog/')


class ForceCORS(MiddlewareMixin):

    def process_response(self, request, response):
        response['Access-Control-Allow-Origin'] = "*"
        return response