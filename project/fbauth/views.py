import urllib

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.shortcuts import redirect


def fbauth(request):
    if request.GET.get('error'):
        error_description = urllib.unquote_plus(
            request.GET.get('error_description')
        )
        messages.error(request, error_description)
        return redirect(settings.FACEBOOK_LOGIN_ERROR_REDIRECT)

    verification_code = request.GET.get('code')

    if not verification_code:
        domain = Site.objects.get_current().domain
        args = {
            'client_id': settings.FACEBOOK_APP_ID,
            'redirect_uri': 'http://' + domain + reverse('fbauth'),
            'scope': ','.join(settings.FACEBOOK_PERMISSIONS_SCOPE),
        }
        return HttpResponseRedirect(
            "https://www.facebook.com/v2.0/dialog/oauth?" +
            urllib.urlencode(args)
        )
    else:
        user = authenticate(verification_code=verification_code)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(
                    settings.FACEBOOK_LOGIN_SUCCESS_REDIRECT
                )
            else:
                messages.error(request, 'Account is disabled.')
        else:
            messages.error(request, 'Facebook login validation failed.')
        return redirect(settings.FACEBOOK_LOGIN_ERROR_REDIRECT)
