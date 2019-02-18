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

def about(request,username):
    return render(request,'profiles/view_schedule.html')