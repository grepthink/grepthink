from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
# Model Imports

# Form Imports
from teamwork.apps.profiles.forms import SignUpForm

# View Imports
from teamwork.apps.profiles.views.EditProfileView import edit_profile

def signup(request):
    """
    public method that generates a form a user uses to sign up for an account (push test)
    """

    page_name = "Signup"
    page_description = "Sign up for Grepthink!"
    title = "Signup"

    GT =  False

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if not form.is_valid():
            return render(request, 'profiles/signup.html',
                          {'form': form})

        else:
            email = form.cleaned_data.get('email')
            split = email.split("@")
            username = split[0]
            password = form.cleaned_data.get('password')
            prof = form.cleaned_data.get('prof')

            if 'grepthink' in email:
                GT = True

            if GT:
                user1 = User.objects.create_superuser(
                    username=username,
                    password=password,
                    email=email)
            else:
                user1 = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email)

            user = authenticate(username=username, password=password)
            login(request, user)

            # saves current user, which creates a link from user to profile
            user1.save()

            if GT:
                user1.profile.isGT = True

            # edits profile to add professor
            user1.profile.isProf = False

            # saves profile
            user1.save()

            return redirect(edit_profile, username)

    else:
        return render(request, 'profiles/signup.html',
                      {'form': SignUpForm(), 'page_name' : page_name,
                      'page_description': page_description, 'title': title})

def profSignup(request):
    """
    public method that generates a form a user uses to sign up for an account (push test)
    """

    page_name = "Signup"
    page_description = "Sign up for Grepthink!"
    title = "Professor Signup"

    GT =  False

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if not form.is_valid():
            return render(request, 'profiles/professorSignup.html',
                          {'form': form})

        else:
            email = form.cleaned_data.get('email')
            split = email.split("@")
            username = split[0]

            if 'grepthink' in email:
                GT = True
            password = form.cleaned_data.get('password')

            if GT:
                user1 = User.objects.create_superuser(
                    username=username,
                    password=password,
                    email=email)
            else:
                user1 = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email)

            user = authenticate(username=username, password=password)
            login(request, user)

            # saves current user, which creates a link from user to profile
            user1.save()

            if GT:
                user1.profile.isGT = True

            # edits profile to add professor
            user1.profile.isProf = True

            # saves profile
            user1.save()

            return redirect(edit_profile, username)

    else:
        return render(request, 'profiles/professorSignup.html',
                      {'form': SignUpForm(), 'page_name' : page_name,
                      'page_description': page_description, 'title': title})

def password_reset(request):
    return

def password_reset_done(request):
    return

def password_reset_confirm(request):
    return

def password_reset_complete(request):
    return
