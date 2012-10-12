from django.contrib import messages
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

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