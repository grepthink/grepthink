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
            User.objects.create_user(username=username, password=password,
                                     email=email)
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')

    else:
        return render(request, 'profiles/signup.html',
                      {'form': SignUpForm()})

@login_required
def profile(request, username):
    """
    Public method that takes a request and a username.  Gets an entered 'skill' from the form
    and stores it in lowercase if it doesn't exist already. Renders profiles/profile.html.

    # TODO: fix up return calls, form should be in if
    """

    form = SkillsForm(request.POST)
    if request.method == 'POST':
        
        if form.is_valid():
            
            skill = form.cleaned_data.get('skill')

            if Skills.objects.filter(skill=skill.lower()):
                # skill already exists
                print("skill already in Skills model")    
            else:
                Skills.objects.create(skill=skill.lower())

        else:                     
            return render(request, 'profiles/profile.html', {
                'page_user': page_user, 'form':form , 
            })


    page_user = get_object_or_404(User, username=username)
    return render(request, 'profiles/profile.html', {
        'page_user': page_user, 'form':form , 
        })















