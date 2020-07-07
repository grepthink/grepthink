from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
# Form Imports
from teamwork.apps.profiles.forms import SignUpForm
# View Imports
from teamwork.apps.profiles.views.EditProfileView import edit_profile

# Model Imports



def signup(request):
    """public method that generates a form a user uses to sign up for an account (push test)"""

    page_name = "Signup"
    page_description = "Sign up for Grepthink!"
    title = "Signup"

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if not form.is_valid():
            print(form.errors)
            return render(request, 'profiles/signup.html',
                          {'form': form})

        else:
            email = form.cleaned_data.get('email')
            split = email.split("@")
            username = find_available_username(split[0])
            password = form.cleaned_data.get('password')

            user1 = User.objects.create_user(
                username=username,
                password=password,
                email=email)

            user = authenticate(username=username, password=password)
            login(request, user)

            # saves current user, which creates a link from user to profile
            user1.save()

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
    """public method that generates a form a user uses to sign up for an account (push test)"""

    page_name = "Signup"
    page_description = "Sign up for Grepthink!"
    title = "Professor Signup"

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if not form.is_valid():
            return render(request, 'profiles/professorSignup.html',
                          {'form': form})

        else:
            email = form.cleaned_data.get('email')
            split = email.split("@")
            username = find_available_username(split[0])
            password = form.cleaned_data.get('password')

            user1 = User.objects.create_user(
                username=username,
                password=password,
                email=email)

            user = authenticate(username=username, password=password)
            login(request, user)

            # saves current user, which creates a link from user to profile
            user1.save()

            # edits profile to add professor
            user1.profile.isProf = True

            # saves profile
            user1.save()

            return redirect(edit_profile, username)

    else:
        return render(request, 'profiles/professorSignup.html',
                      {'form': SignUpForm(), 'page_name' : page_name,
                      'page_description': page_description, 'title': title})

def find_available_username(username):
    """
    Finds the next available username.

    Args:
        username (str): The desired username

    Returns:
        str: The desired username w/ the next available number appended to the end.
    """

    # Find users with that username in descending order
    existing_users = User.objects.filter(username__istartswith=username).order_by('-username')

    # if we found users, parse out value from the highest username
    if existing_users:
        # since we are in desc order, this is always the first user
        user = existing_users[0]

        # parse out the int value applied to the end of username
        value = parse_username_num(user, username)
        if value is None:
            value = 0

        # add 1 to the found value and append it to the username
        return "{}{}".format(username, value + 1)

    return username

def parse_username_num(user, username_to_parse):
    """
    Parses out the number at the end of a user's username given the base username w/o the number.

    Args:
        user (User): The User object which we are parsing the number from.
        username_to_parse (str): The core of the username, before any numbers appended to the end.

    Returns:
        int: On Success, the value parsed.
        None: On Fail or when a number doesn't exist. I.e this is the 2nd user to want this username.
    """
    try:
        return int(user.username[len(username_to_parse):])
    except ValueError:
        return None

def password_reset(request):
    return

def password_reset_done(request):
    return

def password_reset_confirm(request):
    return

def password_reset_complete(request):
    return
