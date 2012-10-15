import datetime

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import utc

from custom.models import Post, Profile

def homepage(request):
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    user = None
    profile = None
    user_referrer = request.session.get('ur', None)
    source_referrer = request.session.get('sr', None)

    if request.user.is_authenticated():
        user = request.user
        profile = user.get_profile()

    site = Site.objects.get_current()
    total_followers_qs = Profile.objects.aggregate(Sum('followers'))
    try:
        total_followers = int(total_followers_qs['followers__sum'])
    except:
        total_followers = 0

    try:
        post = Post.objects.filter(published_date__lte=now).order_by('-published_date')[0]
    except:
        post = None

    dict_context = {
        'user': user,
        'user_referrer': user_referrer,
        'source_referrer': source_referrer,
        'site': site,
        'total_followers': total_followers,
        'post': post,
    }
    return render(request, 'homepage.html', dict_context)

def signout(request):
    logout(request)
    messages.success(request, 'Thanks for visiting us today.')
    return redirect(reverse('homepage'))

def post(request, slug=None):
    utc_now = datetime.datetime.utcnow().replace(tzinfo=utc)

    if request.user.is_staff:
        post = get_object_or_404(Post, slug=slug)
    else:
        post = get_object_or_404(Post, slug=slug, published_date__lte=utc_now)

    return render(request, 'post/post.html', {'post': post})