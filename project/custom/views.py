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
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import simplejson as json
from django.utils.timezone import utc

from custom.forms import EmailForm, SettingsForm
from custom.models import Post, Profile

def homepage(request):
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    profile = None
    settings_form = None
    user_referrer = request.session.get('ur', None)
    user_referrer_profile = None
    display_profile = None
    display_user_pk = request.GET.get('du')
    source_referrer = request.session.get('sr', None)
    absolute_uri = request.build_absolute_uri()

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
        settings_form = SettingsForm(initial=settings_form_initial, user=request.user)

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

    try:
        post = Post.objects.filter(homepage=True, published_date__lte=now).order_by('-published_date')[0]
    except:
        post = None

    recent_posts = Post.objects.filter(homepage=True, published_date__lte=now).order_by('-published_date')
    if post:
        recent_posts = recent_posts.exclude(pk=post.pk)
    recent_posts = recent_posts[:4]

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
        'recent_posts': recent_posts,
        'FACEBOOK_APP_NAMESPACE': settings.FACEBOOK_APP_NAMESPACE,
        'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID,
        'absolute_uri': absolute_uri,
    }

    response = render(request, 'homepage.html', dict_context)
    if request.user.is_authenticated():
        expire_date = now + datetime.timedelta(days=30)
        response.set_cookie('returning_user', value=True, expires=expire_date, httponly=False)
    return response

def signout(request):
    logout(request)
    messages.success(request, 'Thanks for visiting us today.')
    return redirect(reverse('homepage'))

def post(request, slug=None):
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    profile = None
    user_referrer = request.session.get('ur', None)
    user_referrer_profile = None
    source_referrer = request.session.get('sr', None)

    if request.user.is_authenticated():
        profile = request.user.get_profile()

    if user_referrer:
        try:
            user_referrer_object = User.objects.get(id=user_referrer)
            user_referrer_profile = user_referrer_object.get_profile()
        except:
            pass

    site = Site.objects.get_current()
    total_followers_qs = Profile.objects.aggregate(Sum('followers'))
    try:
        total_followers = int(total_followers_qs['followers__sum'])
    except:
        total_followers = 0

    if request.user.is_staff:
        post = get_object_or_404(Post, slug=slug)
    else:
        post = get_object_or_404(Post, slug=slug, published_date__lte=now)

    recent_posts = Post.objects.filter(published_date__lte=now).exclude(pk=post.pk).order_by('-published_date')[:4]

    dict_context = {
        'profile': profile,
        'user_referrer': user_referrer,
        'user_referrer_profile': user_referrer_profile,
        'source_referrer': source_referrer,
        'site': site,
        'total_followers': total_followers,
        'post': post,
        'recent_posts': recent_posts,
    }

    return render(request, 'post/post.html', dict_context)

@login_required
def ajax_email_form(request):
    if request.method == 'POST' and request.is_ajax():
        form = EmailForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            form.save()
            return HttpResponse(json.dumps('success'), mimetype="application/json")
        else:
            return HttpResponseBadRequest(json.dumps(form.errors), mimetype="application/json")

    return HttpResponseBadRequest(json.dumps('Invalid request.'), mimetype="application/json")

@login_required
def ajax_settings_form(request):
    if request.method == 'POST' and request.is_ajax():
        form = SettingsForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            form.save()
            return HttpResponse(json.dumps('success'), mimetype="application/json")
        else:
            return HttpResponseBadRequest(json.dumps(form.errors), mimetype="application/json")

    return HttpResponseBadRequest(json.dumps('Invalid request.'), mimetype="application/json")
