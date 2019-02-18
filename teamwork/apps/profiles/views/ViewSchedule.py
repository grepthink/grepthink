from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

# Model Imports
from teamwork.apps.profiles.models import Profile
from django.http import HttpResponse

# Model Imports
from teamwork.apps.profiles.models import Profile, Events
from teamwork.apps.projects.models import dayofweek

import json

def load_schedule(request,username):
    user= get_object_or_404(User,username=username)
    page_name="View Schedule"
    page_description= "Viewing %s's Schedule"%(username)
    title="View Schedule"
    profile = Profile.objects.filter(user__username=username).first()
    print(profile)

    readable = ""
    if profile.jsonavail:
        jsonDec = json.decoder.JSONDecoder()
        readable = jsonDec.decode(profile.jsonavail)

    meetings = mark_safe(profile.jsonavail)
    print(meetings)

    return render(request,'profiles/view_schedule.html',{'page_username':username,'page_name' : page_name, 'page_description': page_description, 'title': title, 'json_events' : meetings})