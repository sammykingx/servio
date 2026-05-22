from core.url_names import PageURLS
from datetime import datetime
from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse, resolve, Resolver404
from django.views.defaults import page_not_found


class PreLaunchMiddleware:
    """
    Redirects all traffic to the waitlist page until LAUNCH_DATE is reached.
    Exempts the waitlist URL itself, static/media files, and optionally admin.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            return self.get_response(request)
        
        if datetime.now() >= settings.LAUNCH_DATE:
            return self.get_response(request)

        path = request.path

        if any(path.startswith(prefix) for prefix in settings.ALLOWED_PATH_PREFIXES):
            return self.get_response(request)

        try:
            match = resolve(path)
            if match.url_name in settings.ALLOWED_PRE_LAUNCH_URL_NAMES:
                return self.get_response(request)
        except Resolver404:
            return page_not_found(request, Http404())

        return redirect(reverse(PageURLS.WAIT_LIST))