import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect
from django.utils import simplejson as json
from django.utils.timezone import utc

from custom.forms import EmailForm, SettingsForm
from custom.models import Post, Profile
from instagallery.models import Image


def homepage(request, post_slug=None):
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    profile = None
    settings_form = None
    user_referrer = request.session.get('ur', None)
    user_referrer_profile = None
    display_profile = None
    display_user_pk = request.GET.get('du')
    source_referrer = request.session.get('sr', None)
    absolute_uri = request.build_absolute_uri()
    instagram_images = Image.objects.order_by('-instagram_id')[:200]

    if display_user_pk:
        try:
            display_profile = Profile.objects.get(user__pk=display_user_pk)
        except Profile.DoesNotExist:
            pass

    if request.user.is_authenticated():
        profile = request.user.get_profile()
        settings_form_initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'enable_facebook_updates': profile.enable_facebook_updates,
            'enable_twitter_updates': profile.enable_twitter_updates,
            'enable_email_updates': profile.enable_email_updates,
        }
        settings_form = SettingsForm(initial=settings_form_initial,
                                     user=request.user)

    if user_referrer:
        try:
            user_referrer_object = User.objects.get(id=user_referrer)
            user_referrer_profile = user_referrer_object.get_profile()
        except:
            pass

    # We need a dashboard and/or nav bar
    if not display_profile:
        if profile:
            display_profile = profile
        elif user_referrer_profile:
            display_profile = user_referrer_profile

    site = Site.objects.get_current()
    total_followers_qs = Profile.objects.aggregate(Sum('followers'))
    try:
        total_followers = int(total_followers_qs['followers__sum'])
    except:
        total_followers = 0

    if not post_slug:
        try:
            post = Post.objects.filter(
                homepage=True,
                published_date__lte=now).order_by('-published_date')[0]
        except:
            post = None
    else:
        try:
            post = Post.objects.get(homepage=True, published_date__lte=now,
                                    slug=post_slug)
        except Post.DoesNotExist:
            post = None

    dict_context = {
        'display_profile': display_profile,
        'profile': profile,
        'settings_form': settings_form,
        'user_referrer': user_referrer,
        'user_referrer_profile': user_referrer_profile,
        'source_referrer': source_referrer,
        'site': site,
        'total_followers': total_followers,
        'post': post,
        'FACEBOOK_APP_NAMESPACE': settings.FACEBOOK_APP_NAMESPACE,
        'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID,
        'absolute_uri': absolute_uri,
        'instagram_images': instagram_images,
    }

    response = render(request, 'homepage.html', dict_context)

    if request.user.is_authenticated():
        expire_date = now + datetime.timedelta(days=30)
        response.set_cookie('returning_user', value=True, expires=expire_date,
                            httponly=False)
    return response


@login_required
def dashboard(request):
    profile = request.user.get_profile()
    settings_form_initial = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'enable_facebook_updates': profile.enable_facebook_updates,
        'enable_twitter_updates': profile.enable_twitter_updates,
        'enable_email_updates': profile.enable_email_updates,
    }
    settings_form = SettingsForm(initial=settings_form_initial,
                                 user=request.user)
    instagram_images = Image.objects.order_by('-instagram_id')[:200]
    return render(request, 'dashboard.html', {
        'profile': profile,
        'settings_form': settings_form,
        'instagram_images': instagram_images,
    })


def signout(request):
    logout(request)
    messages.success(request, 'Thanks for visiting us today.')
    return redirect(reverse('homepage'))


def signin(request):
    if request.user.is_authenticated():
        return redirect(reverse('dashboard'))
    return render(request, 'signin.html')


@login_required
def ajax_email_form(request):
    if request.method == 'POST' and request.is_ajax():
        form = EmailForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponse(json.dumps('success'),
                                mimetype="application/json")
        else:
            return HttpResponseBadRequest(json.dumps(form.errors),
                                          mimetype="application/json")

    return HttpResponseBadRequest(json.dumps('Invalid request.'),
                                  mimetype="application/json")


@login_required
def ajax_settings_form(request):
    if request.method == 'POST' and request.is_ajax():
        form = SettingsForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponse(json.dumps('success'),
                                mimetype="application/json")
        else:
            return HttpResponseBadRequest(json.dumps(form.errors),
                                          mimetype="application/json")

    return HttpResponseBadRequest(json.dumps('Invalid request.'),
                                  mimetype="application/json")
