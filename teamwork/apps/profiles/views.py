import json

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect, JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from teamwork.apps.profiles.forms import SignUpForm
from teamwork.apps.projects.models import *

from .forms import *
from .models import *
from django.urls import reverse


def signup(request):
    """
    public method that generates a form a user uses to sign up for an account (push test)
    """

    page_name = "Signup"
    page_description = "Sign up for Grepthink!"
    title = "Signup"

    GT = False

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if not form.is_valid():
            return render(request, 'profiles/signup.html',
                          {'form': form})

        else:
            email = form.cleaned_data.get('email')
            split = email.split("@")
            username = split[0]

            if 'grepthink' in email:
                GT = True
            password = form.cleaned_data.get('password')

            prof = form.cleaned_data.get('prof')
            
            if GT:
                user1 = User.objects.create_superuser(
                    username=username,
                    password=password,
                    email=email)
            else:
                # parse email for 'username'
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


@login_required
def view_profile(request, username):
    """
    Public method that takes a request and a username.  Gets an entered 'skill' from the form
    and stores it in lowercase if it doesn't exist already. Renders profiles/profile.html.

    """
    page_user = get_object_or_404(User, username=username)
    user = request.user
    profile = Profile.objects.get(user=user)
    page_name = "Profile"
    page_description = "%s's Profile" % page_user.username
    title = "View Profile"

    # gets all interest objects of the current user
    my_interests = Interest.objects.filter(user=user)
    # gets all projects where user has interest
    my_projects = Project.objects.filter(interest__in=my_interests)

    return render(request, 'profiles/profile.html', {
        'page_user': page_user, 'profile': profile, 'page_name': page_name, 'page_description': page_description,
        'title': title
    })


def edit_skills(request, username):
    if request.method == 'GET' and request.is_ajax():
        # JSON prefers dictionaries over lists.
        data = dict()
        # A list in a dictionary, accessed in select2 ajax
        data['items'] = []
        q = request.GET.get('q')
        if q is not None:
            results = Skills.objects.filter(
                Q(skill__contains=q)).order_by('skill')
        for s in results:
            data['items'].append({'id': s.skill, 'text': s.skill})
        return JsonResponse(data)

    return HttpResponse("Failure")


@login_required
def edit_profile(request, username):
    """
    Public method that takes a request and a username.  Gets an entered 'skill' from the form
    and stores it in lowercase if it doesn't exist already. Renders profiles/edit_profile.html.
    """

    if not request.user.is_authenticated:
        return redirect('profiles/profile.html')
    if request.user.profile.isGT:
        tempProfile = User.objects.get(username=username)
        profile = Profile.objects.get(user=tempProfile)
    else:
        # grab profile for the current user
        profile = Profile.objects.get(user=request.user)

    if request.user.profile.isGT:
        pass
    elif request.user.username != username:
        messages.info(request, 'You cannot access the user profile specified!')
        return redirect(view_profile, request.user.username)

    page_name = "Edit Profile"
    page_description = "Edit %s's Profile" % profile.user.username
    title = "Edit Profile"

    # original form
    if request.method == 'POST':

        # Add skills to the project learn_skills
        if request.POST.get('known_skills') or request.POST.get('learn_skills'):
            known = request.POST.getlist('known_skills')
            learn = request.POST.getlist('learn_skills')
            if known:
                for s in known:
                    s_lower = s.lower()
                    # Check if lowercase version of skill is in db
                    if Skills.objects.filter(skill=s_lower):
                        # Skill already exists, then pull it up
                        known_skill = Skills.objects.get(skill=s_lower)
                    else:
                        # Add the new skill to the Skills table
                        known_skill = Skills.objects.create(skill=s_lower)
                        # Save the new object
                        known_skill.save()
                    # Add the skill to the project (as a desired_skill)
                    profile.known_skills.add(known_skill)
                    profile.save()
                # handles saving bio information also
                edit_profile_helper(request, username)
            if learn:
                for s in learn:
                    s_lower = s.lower()
                    # Check if lowercase version of skill is in db
                    if Skills.objects.filter(skill=s_lower):
                        # Skill already exists, then pull it up
                        learn_skill = Skills.objects.get(skill=s_lower)
                    else:
                        # Add the new skill to the Skills table
                        learn_skill = Skills.objects.create(skill=s_lower)
                        # Save the new object
                        learn_skill.save()
                    # Add the skill to the project (as a desired_skill)
                    profile.learn_skills.add(learn_skill)
                    profile.save()
                # handles saving bio information also
                edit_profile_helper(request, username)
            # stay on edit_profile page
            return redirect(edit_profile, username)

        # handle removing a known skill
        if request.POST.get('known_remove'):
            skillname = request.POST.get('known_remove')
            to_delete = Skills.objects.get(skill=skillname)
            profile.known_skills.remove(to_delete)

            # handles saving bio information also
            edit_profile_helper(request, username)
            # stay on edit_profile page
            return redirect(edit_profile, username)

        # handle removing a skill they wanted to learn
        if request.POST.get('learn_remove'):
            skillname = request.POST.get('learn_remove')
            to_delete = Skills.objects.get(skill=skillname)
            profile.learn_skills.remove(to_delete)

            # handles saving bio information also
            edit_profile_helper(request, username)
            # stay on edit_profile page
            return redirect(edit_profile, username)

        # handle deleting avatar
        if request.POST.get('delete_avatar'):
            avatar = request.POST.get('delete_avatar')
            profile.avatar.delete()
            form = ProfileForm(instance=profile)

        # handle deleting profile
        if request.POST.get('delete_profile'):
            page_user = get_object_or_404(User, username=username)
            page_user.delete()
            if request.user.profile.isGT:
                return redirect('view_course')
            else:
                return redirect('about')

        # handles saving bio info if none of the cases were taken

        form = edit_profile_helper(request, username)
        if form.is_valid():
            # redirects to view_profile when submit button is clicked
            return redirect(view_profile, username)

    else:
        # load form with prepopulated data
        form = ProfileForm(instance=profile)

    known_skills_list = profile.known_skills.all()
    learn_skills_list = profile.learn_skills.all()

    # form.fields.

    page_user = get_object_or_404(User, username=username)
    return render(request, 'profiles/edit_profile.html', {
        'page_user': page_user, 'form': form, 'profile': profile,
        'known_skills_list': known_skills_list,
        'learn_skills_list': learn_skills_list, 'page_name': page_name, 'page_description': page_description,
        'title': title})


def edit_profile_helper(request, username):
    """
        Helper function that saves profile information from the ProfileForm
    """

    if request.user.profile.isGT:
        tempProfile = User.objects.get(username=username)
        profile = Profile.objects.get(user=tempProfile)
    else:
        # grab profile for the current user
        profile = Profile.objects.get(user=request.user)

    # request.FILES is passed for File storing
    form = ProfileForm(request.POST, request.FILES)
    if form.is_valid():

        # grab each form element from the clean form
        bio = form.cleaned_data.get('bio')
        email = form.cleaned_data.get('email')
        name = form.cleaned_data.get('name')
        institution = form.cleaned_data.get('institution')
        location = form.cleaned_data.get('location')
        ava = form.cleaned_data.get('avatar')

        # if data is entered, save it to the profile for the following
        if name:
            profile.name = name
            profile.save()
        if email:
            user = request.user
            user.email = email
            user.save()
        if bio:
            profile.bio = bio
            profile.save()
        if institution:
            profile.institution = institution
            profile.save()
        if location:
            profile.location = location
            profile.save()
        if ava:
            profile.avatar = ava
            profile.save()

    return form


@login_required
def edit_schedule(request, username):
    """
    Public method that takes a request and a username.
    Gets a list of 'events' from a calendar and stores the event as an array of tuples
    Redners profiles/edit_calendar.html
    """
    from django.utils.safestring import mark_safe

    user = get_object_or_404(User, username=username)
    page_name = "Edit Schedule"
    page_description = "Edit %s's Schedule" % (user.username)
    title = "Edit Schedule"
    profile = Profile.objects.get(user=user)

    # gets current avaliability
    readable = ""
    if profile.jsonavail:
        jsonDec = json.decoder.JSONDecoder()
        readable = jsonDec.decode(profile.jsonavail)

    meetings = mark_safe(profile.jsonavail)

    return render(request, 'profiles/edit_schedule.html',
                  {'page_name': page_name, 'page_description': page_description, 'title': title,
                   'json_events': meetings})


@csrf_exempt
def save_event(request, username):
    # grab profile for the current user
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':

        if request.POST.get('Clear'):
            profile.jsonavail = ""
            profile.save()

            # If user already has a schedule, delete it
            if profile.avail.all() is not None: profile.avail.all().delete()

            profile.save()

            print("\n\nI CLEARED THE SCHEDULE\n")

            return HttpResponse("Schedule Cleared")

        # List of events as a string (json)
        jsonEvents = request.POST.get('jsonEvents')

        # Load json event list into a python list of dicts
        event_list = json.loads(jsonEvents)

        profile.jsonavail = json.dumps(event_list)
        profile.save()

        # If user already has a schedule, delete it
        if profile.avail.all() is not None: profile.avail.all().delete()

        # For each event
        for event in event_list:
            # Create event object
            busy = Events()

            # Get data
            # function assumes start day and end day are the same
            day = event['start'][8] + event['start'][9]
            day = int(day)
            s_hour = event['start'][11] + event['start'][12]
            s_minute = event['start'][14] + event['start'][15]

            s_hour = int(s_hour)
            s_minute = int(s_minute)

            e_hour = event['end'][11] + event['end'][12]
            e_minute = event['end'][14] + event['end'][15]
            e_hour = int(e_hour)
            e_minute = int(e_minute)

            # Assign data
            busy.day = dayofweek(day)
            busy.start_time_hour = s_hour
            busy.start_time_min = s_minute
            busy.end_time_hour = e_hour
            busy.end_time_min = e_minute

            # Save event
            busy.save()

            profile.avail.add(busy)
            profile.save()

        return HttpResponse("Schedule Saved")
        # return HttpResponse(json.dumps({'eventData' : eventData}), content_type="application/json")

    else:
        pass
        # print("\n\nDebug: Request method was not post \n\n")

    return HttpResponse("Failure")


@login_required
def view_alerts(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    page_name = "Alerts"
    page_description = "Your notifications"

    unread = profile.unread_alerts()
    archive = profile.read_alerts()

    return render(request, 'profiles/alerts.html', {
        'profile': profile,
        'unread': unread,
        'archive': archive,
        'page_name': page_name,
        'page_description': page_description
    })


@login_required
def read_alert(request, ident):
    user = request.user
    alert = get_object_or_404(Alert, id=ident)
    if alert.to.id is user.id:
        alert.read = True
        alert.save()
        # else:
        # print("Attempt to read alert caught by internet police: " + str(alert.id))
    return redirect(view_alerts)


@login_required
def unread_alert(request, ident):
    user = request.user
    alert = get_object_or_404(Alert, id=ident)
    if alert.to.id is user.id:
        alert.read = False
        alert.save()
    return redirect(view_alerts)


@login_required
def archive_alerts(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    unread = profile.unread_alerts()

    for alert in unread:
        if alert.to.id is user.id:
            alert.read = True
            alert.save()

    return redirect(view_alerts)


@login_required
def delete_alert(request, ident):
    user = request.user
    alert = get_object_or_404(Alert, id=ident)
    if alert.to.id is user.id and alert.read is True:
        alert.delete()
    return redirect(view_alerts)
