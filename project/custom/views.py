import datetime

from django.contrib import messages
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import utc

from custom.models import Post

def homepage(request):
    user = None
    profile = None

    if request.user.is_authenticated():
        user = request.user
        profile = user.get_profile()

    dict_context = {
        'user': user,
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