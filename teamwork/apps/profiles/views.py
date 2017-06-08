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
    public method that generates a form a user uses to sign up for an account
    """

    page_name = "Signup"
    page_description = "Sign up for Groupthink!"
    title = "Signup"

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
                      {'form': SignUpForm(), 'page_name' : page_name, 'page_description': page_description, 'title': title})

@login_required
def view_profile(request, username):
    """
    Public method that takes a request and a username.  Gets an entered 'skill' from the form
    and stores it in lowercase if it doesn't exist already. Renders profiles/profile.html.

    """
    user = request.user
    profile = Profile.objects.get(user=user)
    page_name = "Profile"
    page_description = "%s's Profile"%(user.username)
    title = "View Profile"

    # gets all interest objects of the current user
    my_interests = Interest.objects.filter(user=user)
    # gets all projects where user has interest
    my_projects = Project.objects.filter(interest__in=my_interests)

    page_user = get_object_or_404(User, username=username)
    return render(request, 'profiles/profile.html', {
        'page_user': page_user, 'profile':profile, 'page_name' : page_name, 'page_description': page_description, 'title': title
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
                Q( skill__contains = q ) ).order_by( 'skill' )
        for s in results:
            data['items'].append({'id': s.skill, 'text': s.skill})
        return JsonResponse(data)


    return HttpResponse("Failure")

@login_required
def edit_profile(request, username):
    """
    Public method that takes a request and a username.  Gets an entered 'skill' from the form
    and stores it in lowercase if it doesn't exist already. Renders profiles/edit_profile.html.

    TODO: screen flashes when deleting skills? Maybe pc just blows
    TODO: test different uses of profile.save(), i.e not so many god damn times
    TODO: Avatar doesn't show current file.url

    """
    if not request.user.is_authenticated:
        return redirect('profiles/profile.html')

    #grab profile for the current user
    profile = Profile.objects.get(user=request.user)

    if request.user.username != username:
        messages.info(request, 'You cannot access the user profile specified!')
        return redirect(view_profile, request.user.username)

    page_name = "Edit Profile"
    page_description = "Edit %s's Profile"%(profile.user.username)
    title = "Edit Profile"

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

            return redirect(edit_profile, username)
        if learn:
            for s in learn:
                s_lower = s.lower()
                # Check if lowercase version of skill is in db
                if Skills.objects.filter(skill=s_lower):
                    # Skill already exists, then pull it up
                    learn_skill = Skills.objects.get(skill=s_lower)
                else:
                    # Add the new skill to the Skills table
                    leanr_skill = Skills.objects.create(skill=s_lower)
                    # Save the new object
                    learn_skill.save()
                # Add the skill to the project (as a desired_skill)
                profile.learn_skills.add(learn_skill)
                profile.save()

            return redirect(edit_profile, username)

    #handle deleting avatar
    if request.POST.get('delete_avatar'):
        avatar = request.POST.get('delete_avatar')
        profile.avatar.delete()
        form = ProfileForm(instance=profile)
    #handle deleting profile
    elif request.POST.get('delete_profile'):
        page_user = get_object_or_404(User, username=username)
        page_user.delete()
        return redirect('about')

    #original form
    elif request.method == 'POST':
        #request.FILES is passed for File storing
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            # grab each form element from the clean form
            # known = form.cleaned_data.get('known_skill')
            # learn = form.cleaned_data.get('learn_skill')
            bio = form.cleaned_data.get('bio')
            name = form.cleaned_data.get('name')
            institution = form.cleaned_data.get('institution')
            location = form.cleaned_data.get('location')
            ava = form.cleaned_data.get('avatar')
            profile.save()
            # # if we have an input in known_skills
            # if known:
            #     # parse known on ','
            #     skill_array = known.split(',')
            #     for skill in skill_array:
            #         stripped_skill = skill.strip()
            #         if not (stripped_skill == ""):
            #             # check if skill is in Skills table, lower standardizes input
            #             if Skills.objects.filter(skill=stripped_skill.lower()):
            #                 # skill already exists, then pull it up
            #                 known_skill = Skills.objects.get(skill=stripped_skill.lower())
            #             else:
            #                 # we have to add the skill to the table
            #                 known_skill = Skills.objects.create(skill=stripped_skill.lower())
            #                 # save the new object
            #                 known_skill.save()
            #
            #             # add the skill to the current profile
            #             profile.known_skills.add(known_skill)
            #             profile.save()
            #
            #
            # # same as Known implemenation for learn_skills
            # if learn:
            #     skill_array = learn.split(',')
            #     for skill in skill_array:
            #         stripped_skill = skill.strip()
            #         if not (stripped_skill == ""):
            #             # check if skill is in Skills table, lower standardizes input
            #             if Skills.objects.filter(skill=stripped_skill.lower()):
            #                 # skill already exists, then pull it up
            #                 learn_skill = Skills.objects.get(skill=stripped_skill.lower())
            #             else:
            #                 # we have to add the skill to the table
            #                 learn_skill = Skills.objects.create(skill=stripped_skill.lower())
            #                 # save the new object
            #                 learn_skill.save()
            #             profile.learn_skills.add(learn_skill)
                        # profile.save()
            #if data is entered, save it to the profile for the following
            if name:
                profile.name = name
                profile.save()
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

        #redirects to view_profile when submit button is clicked
        return redirect(view_profile, username)

    else:
        #load form with prepopulated data
        form = ProfileForm(instance=profile)

    # known_skills_list = profile.known_skills.all()
    # learn_skills_list = profile.learn_skills.all()
    page_user = get_object_or_404(User, username=username)

    # return render(request, 'profiles/edit_profile.html', {
    #     'page_user': page_user, 'form':form, 'profile':profile,
    #     'known_skills_list':known_skills_list,
    #     'learn_skills_list':learn_skills_list, 'page_name' : page_name, 'page_description': page_description, 'title': title })
    return render(request, 'profiles/edit_profile.html', {
        'page_user': page_user, 'form':form, 'profile':profile,
        'page_name' : page_name, 'page_description': page_description, 'title': title })

@login_required
def edit_schedule(request, username):
    """
    Public method that takes a request and a username.
    Gets a list of 'events' from a calendar and stores the event as an array of tuples
    Redners profiles/edit_calendar.html

    TODO: The whole shebang

    """
    user = get_object_or_404(User, username=username)
    page_name = "Edit Schedule"
    page_description = "Edit %s's Schedule"%(user.username)
    title = "Edit Schedule"

    return render(request, 'profiles/edit_schedule.html', {'page_name' : page_name, 'page_description': page_description, 'title': title })

@csrf_exempt
def save_event(request, username):
    #grab profile for the current user
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST' and request.is_ajax():

        # List of events as a string (json)
        jsonEvents = request.POST.get('jsonEvents')

        # Load json event list into a python list of dicts
        event_list = json.loads(jsonEvents)

        # If user already has a schedule, delete it
        if profile.avail.all() is not None: profile.avail.all().delete()

        # For each event
        for event in event_list:
            # Create event object
            busy = Events()

            # Get data
            #function assumes start day and end day are the same
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
        #return HttpResponse(json.dumps({'eventData' : eventData}), content_type="application/json")

    else:
        pass
        #print("\n\nDebug: Request method was not post \n\n")

    return HttpResponse("Failure")

@login_required
def view_alerts(request):

    user = request.user
    profile = Profile.objects.get(user=user)

    page_name = "Alerts"
    page_description = "Your notifications"

    # Testing by injecting alerts every time
    #extra = Alert()
    #extra.sender = user
    #extra.to = user
    #extra.msg = "You viewed your alerts"
    #extra.url = reverse('profile', args=[user.username])
    #extra.save()

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
def delete_alert(request, ident):
    user = request.user
    alert = get_object_or_404(Alert, id=ident)
    if alert.to.id is user.id and alert.read is True:
        alert.delete()
    return redirect(view_alerts)
