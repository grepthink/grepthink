# Django Imports
from __future__ import print_function
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.http import HttpResponse
# Model Imports
from teamwork.apps.profiles.models import Profile
# Be careful for this one, it may effect the Refresh feature
from django.http import HttpResponseRedirect
# For Refresh feature step 12
from django.http import HttpResponse, JsonResponse

# Model Imports
from teamwork.apps.profiles.models import Profile, Events,Credentials
from teamwork.apps.projects.models import dayofweek
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.discovery import build
from itertools import *

# Form Imports

# View Imports

# Other Imports
import json
import httplib2
import os
import datetime
import requests
import google.oauth2.credentials

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
flags = tools.argparser.parse_args([])

@login_required
def edit_schedule(request, username):
    """
    Public method that takes a request and a username.
    Gets a list of 'events' from a calendar and stores the event as an array of tuples
    Redners profiles/edit_calendar.html
    """

    user = get_object_or_404(User, username=username)
    page_name = "Edit Schedule"
    page_description = "Edit %s's Schedule"%(user.username)
    title = "Edit Schedule"
    profile = Profile.objects.get(user=user)
    this_user=request.user.username
    #gets current avaliability
    readable = ""
    if profile.jsonavail:
        jsonDec = json.decoder.JSONDecoder()
        readable = jsonDec.decode(profile.jsonavail)

    meetings = mark_safe(profile.jsonavail)
    
    if(profile.isProf==True):
        is_prof=True
    else:
        is_prof=False

    return render(request, 'profiles/edit_schedule.html', {'page_name' : page_name, 'page_description': page_description, 'title': title, 'json_events' : meetings,'this_user':this_user,'is_Prof':is_prof})

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
        print("Edit schedule " +profile.jsonavail)
        profile.save()

        # If user already has a schedule, delete it
        if profile.avail.all() is not None: profile.avail.all().delete()

        # For each event
        # for event in event_list:
        #     # Create event object
        #     busy = Events()

        #     # Get data
        #     #function assumes start day and end day are the same
        #     day = event['start'][8] + event['start'][9]
        #     day = int(day)
        #     s_hour = event['start'][11] + event['start'][12]
        #     s_minute = event['start'][14] + event['start'][15]

        #     s_hour = int(s_hour)
        #     s_minute = int(s_minute)

        #     e_hour = event['end'][11] + event['end'][12]
        #     e_minute = event['end'][14] + event['end'][15]
        #     e_hour = int(e_hour)
        #     e_minute = int(e_minute)

        #     # Assign data
        #     busy.day = dayofweek(day)
        #     busy.start_time_hour = s_hour
        #     busy.start_time_min = s_minute
        #     busy.end_time_hour = e_hour
        #     busy.end_time_min = e_minute

        #     # Save event
        #     busy.save()

        #     profile.avail.add(busy)
        #     profile.save()


        return HttpResponse("Schedule Saved")
        #return HttpResponse(json.dumps({'eventData' : eventData}), content_type="application/json")

    return HttpResponse("Failure")

# For Refresh feature step 13
@csrf_exempt
def refresh_schedule(request, username):

    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)

    #gets current avaliability
    readable = ""
    if profile.jsonavail:
        jsonDec = json.decoder.JSONDecoder()
        readable = jsonDec.decode(profile.jsonavail)

    meetings = mark_safe(profile.jsonavail)

    return JsonResponse(meetings,safe=False, json_dumps_params={'ensure_ascii': False})

@login_required
def import_schedule(request,username):
    service, credentials = get_credentials(username)    #otain credentials if it's non-existed
    
    result_events = get_calendar(credentials,service) #obtain list of calendar events
    events_list=[]
    for event in result_events:         # append calendar information into the list with corrected format for FullCalendar
        title= event['summary']
        if(event['start'].get('dateTime') is not None):             #get timed events from Google Calendar
            start=event['start'].get('dateTime')
            end=event['end'].get('dateTime')
            start=start[:-6]
            end=end[:-6]
            this_event={'title':title,'start':start,'end':end}       
        else:
            start=event['start'].get('date')                        #get all-day events from Google
            end=event['end'].get('date')
            this_event={'title':title,'start':start,'end':end}                                                             
        
        events_list.append(this_event)                             


    profile = Profile.objects.get(user=request.user)
    string_profile = json.loads(profile.jsonavail)
    
    profile.jsonavail = '[]'                #Empty profile.jsonavail
    profile.save()
               
    google_events=json.loads(json.dumps(events_list))       

    #save calendar events into profile.jsonavail
    profile.jsonavail = json.dumps(string_profile+google_events)
    profile.save()    
    return HttpResponseRedirect("/")
 
def get_calendar(credentials,service):

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=250, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events


@login_required
def export_schedule(request,username):
    service, credentials = get_credentials(username) #obtain credentials if it's non-existed

    profile = Profile.objects.get(user=request.user)
    readable=""
    if profile.jsonavail:
        jsonDec = json.decoder.JSONDecoder()
        readable = jsonDec.decode(profile.jsonavail)

    #put data from profile.jsonavail into google calendar format and send
    EVENT={'summary':'','start':{'dateTime':''},'end':{'dateTime':''}}
    EVENT_all={'summary':'','start':{'date':''},'end':{'date':''}}
    for event in readable:
        if('T' in event['start'] or 'T' in event['end']):
            EVENT['summary']=event['title']
            EVENT['start']['dateTime']=event['start']+'-07:00'
            EVENT['end']['dateTime']=event['end']+'-07:00'
            send=service.events().insert(calendarId='primary',sendNotifications=True,body=EVENT).execute()
        else:
            EVENT_all['summary']=event['title']
            EVENT_all['start']['date']=event['start']
            EVENT_all['end']['date']=event['end']
            send=service.events().insert(calendarId='primary',sendNotifications=True,body=EVENT_all).execute()
       
    return HttpResponseRedirect("/")

def credentials_to_dict(credentials):
      return {'access_token': credentials.access_token,
          'refresh_token': credentials.refresh_token,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes,
          'invalid': credentials.invalid}

def get_credentials(username):
    usr=User.objects.get(username=username)
    store = Storage('storage.json')
    creden=Credentials.objects.filter(user=usr).first()
# 
    if (creden):    #if creden existed
        if (not creden.invalid):   #and if creden valid, request new access token using refresh_token
            payload={'refresh_token':creden.refresh_token,'client_id':creden.client_id,'client_secret':creden.client_secret,'grant_type':'refresh_token'}
            r=requests.post('https://oauth2.googleapis.com/token',data=payload)
            new_token=json.loads(r.text)
            credentials = google.oauth2.credentials.Credentials(
                token=new_token['access_token'],
                refresh_token=creden.refresh_token ,
                id_token=None,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=creden.client_id,
                client_secret=creden.client_secret)
            creden.access_token=new_token['access_token']
            creden.save()
            service=build('calendar','v3',credentials=credentials)
            return (service,credentials)
        else:
            creden.delete()
    # If no creden existed
    flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    credentials = tools.run_flow(flow, store,flags)
    os.remove('storage.json')
    cred = credentials_to_dict(credentials)
    creden=Credentials.objects.create(user=usr,access_token=cred['access_token'],refresh_token=cred['refresh_token'],client_id=cred['client_id'],client_secret=cred['client_secret'],scopes=cred['scopes'],invalid=cred['invalid'])
    creden.save()
    http = credentials.authorize(httplib2.Http())
    service = build('calendar', 'v3', http=http)
    return (service,credentials)


@csrf_exempt
def save_time_limit(request, username):
    #grab profile for the current user
    profile = Profile.objects.get(user=request.user)
    if(profile.isProf==True):
        if(request.method == 'POST'):
            time = request.POST.get('time')
            time_limit=int(json.loads(time))
            profile.meeting_limit=time_limit
            profile.save()
            return HttpResponse("Set Meeting Time Limit")
    else:
        return HttpResponse('Wrong user category')       

@login_required
def revoke_access(request,username):
    usr=User.objects.get(username=username)
    credential=Credentials.objects.filter(user=usr).first()
    if(credential):
        credential.delete()
        return HttpResponseRedirect("/")
    else:
        return HttpResponse("No user Google's credential found")
    
