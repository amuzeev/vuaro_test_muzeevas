# -*- encoding: utf-8 -*-

from re import compile

from django.http import HttpResponseRedirect
from django.conf import settings


EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


class LoginRequiredMiddleware:
    def process_request(self, request):
        if not request.user.is_authenticated():            
            if request.path_info != u'/':
                path = request.path_info.lstrip('/')
                if not any(m.match(path) for m in EXEMPT_URLS):
                    #return HttpResponseRedirect("%s?next=%s" % (settings.LOGIN_URL, request.path_info))
                    return HttpResponseRedirect(settings.LOGIN_URL)


