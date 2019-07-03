# For Refresh feature step 14
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
# Model Imports
from teamwork.apps.profiles.models import Profile
from django.http import HttpResponse

# Model Imports
from teamwork.apps.profiles.models import Profile, Events,Alert
from teamwork.apps.projects.models import dayofweek
from teamwork.apps.courses.models import Assignment
import json

def load_calendar(request,slug):
    
    user=request.user
    assigns = Assignment.objects.filter(course_Name=slug)
    assignments=[]
    for ass in assigns:
        ass={
            'title':ass.ass_name + ': ' + ass.description,
            'start':ass.due_date.isoformat(),
            'description':ass.description
        }
        assignments.append(ass)
    
    assignments=json.dumps(assignments)
    assignments=mark_safe(assignments)
    print(assignments)

    return render(request,'courses/course_calendar.html',{'slug':slug, 'page_user':user,'assignments':assignments});