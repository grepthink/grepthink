from .models import *
from .forms import *

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from teamwork.apps.profiles.forms import SignUpForm


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if not form.is_valid():
            return render(request, 'profiles/signup.html',
                          {'form': form})

        else:
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            prof = form.cleaned_data.get('prof')

            user1 = User.objects.create_user(username=username, password=password,
                                     email=email)
            user = authenticate(username=username, password=password)
            login(request, user)

            # saves current user, which creates a link from user to profile
            user1.save()

            # edits profile to add professor
            user1.profile.isProf = prof

            # saves profile
            user1.save()

            #User.objects.save()


            #uinfo = user.get_profile()
            #uinfo.isProf = prof
            #uinfo.save()

            return redirect('/')

    else:
        return render(request, 'profiles/signup.html',
                      {'form': SignUpForm()})

@login_required
def profile(request, username):
    page_user = get_object_or_404(User, username=username)
    return render(request, 'profiles/profile.html', {
        'page_user': page_user,
        })
