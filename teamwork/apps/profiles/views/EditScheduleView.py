# Django Imports
# Other Imports
import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
# Model Imports
# Model Imports
from teamwork.apps.profiles.models import Events, Profile
from teamwork.apps.projects.models import dayofweek

# Form Imports

# View Imports


@login_required
def edit_schedule(request, username):
    """
    Public method that takes a request and a username.

    Gets a list of 'events' from a calendar and stores the event as an array of tuples Redners
    profiles/edit_calendar.html
    """

    user = get_object_or_404(User, username=username)
    page_name = "Edit Schedule"
    page_description = "Edit %s's Schedule"%(user.username)
    title = "Edit Schedule"
    profile = Profile.objects.get(user=user)

    #gets current avaliability
    readable = ""
    if profile.jsonavail:
        jsonDec = json.decoder.JSONDecoder()
        readable = jsonDec.decode(profile.jsonavail)

    meetings = mark_safe(profile.jsonavail)

    return render(request, 'profiles/edit_schedule.html', {'page_name' : page_name, 'page_description': page_description, 'title': title, 'json_events' : meetings})

@csrf_exempt
def save_event(request, username):
    #grab profile for the current user
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':

        if request.POST.get('Clear'):
            profile.jsonavail = ""
            profile.save()

            # If user already has a schedule, delete it
            if profile.avail.all() is not None: profile.avail.all().delete()

            profile.save()
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

    return HttpResponse("Failure")
