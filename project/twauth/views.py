import tweepy

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

def twauth(request):
    oauth_verifier = request.GET.get('oauth_verifier')
    domain = Site.objects.get_current().domain
    callback_url = 'http://' + domain + reverse('twauth')

    if not oauth_verifier:
        try:
            auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET, callback_url)
            redirect_url = auth.get_authorization_url(signin_with_twitter=True)
            request.session['tw_request_token'] = (auth.request_token.key, auth.request_token.secret)
            return HttpResponseRedirect(redirect_url)
        except:
            messages.error(request, 'Twitter authentication failed.')
            return redirect(settings.TWITTER_LOGIN_ERROR_REDIRECT)
    else:
        token = request.session.get('tw_request_token', None)
        if not token:
            messages.error(request, 'Twitter authentication failed.')
            return redirect(settings.TWITTER_LOGIN_ERROR_REDIRECT)

        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET, callback_url)
        del request.session['tw_request_token']
        auth.set_request_token(token[0], token[1])

        # Retrieve access token and store
        try:
            auth.get_access_token(oauth_verifier)
        except tweepy.TweepError:
            messages.error(request, 'Twitter authentication failed.')
            return redirect(settings.TWITTER_LOGIN_ERROR_REDIRECT)

        user = authenticate(oauth_handler=auth)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(settings.TWITTER_LOGIN_SUCCESS_REDIRECT)
            else:
                messages.error(request, 'Account is disabled')
                return redirect(settings.TWITTER_LOGIN_ERROR_REDIRECT)
        else:
            messages.error(request, 'Twitter authentication failed.')
            return redirect(settings.TWITTER_LOGIN_ERROR_REDIRECT)