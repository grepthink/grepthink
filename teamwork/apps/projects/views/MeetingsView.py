from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

import json

from teamwork.apps.projects.models import Project
from teamwork.apps.courses.models import Course
from teamwork.apps.projects.models import dayofweek
from teamwork.apps.projects.forms import *
from django.utils.safestring import mark_safe

@login_required
def view_meetings(request, slug):
    """
    Public method that takes a request and a slug, retrieves the Project object
    from the model with given project slug.  Renders projects/view_project.html

    Passing status check unit test in test_views.py.
    """
    project = get_object_or_404(Project, slug=slug)
    
    # Populate with project name and tagline
    page_name = project.title or "Project"
    page_description = project.tagline or "Meeting Times"
    title = project.title or "Meetings"

    find_meeting(slug)

    readable = ""
    if project.readable_meetings:
        jsonDec = json.decoder.JSONDecoder()
        readable = jsonDec.decode(project.readable_meetings)

    # Get the course given a project wow ethan great job keep it up.
    course = Course.objects.get(projects=project)

    #meetings = mark_safe([{'start': '2017-04-09T08:00:00', 'end': '2017-04-09T20:30:00', 'title': 'Meeting'}])
    meetings = mark_safe(project.meetings)

    return render(request, 'projects/meeting_times.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title,
        'project': project, 'course' : course, 'json_events': meetings})

def find_meeting(slug):
    """
    Find and store possible meeting time for a given project
    """
    # Gets current project
    project = get_object_or_404(Project, slug=slug)
    # course = Course.objects.get(projects=project)
    # low = project.lower_time_bound
    # high = project.upper_time_bound

    # If project already has a list of meeting times, delete it
    if project.meetings is not None:
        project.meetings = ''
    if project.readable_meetings is not None:
         project.readable_meetings = ''

    # Stores avaliablity in list
    # event_list = project.generate_avail(low, high)
    event_list = project.generate_avail()
    readable_list = []

    for event in event_list:

        day = event['start'][8] + event['start'][9]
        day = int(day)
        day = dayofweek(day)
        s_hour = event['start'][11] + event['start'][12]
        s_minute = event['start'][14] + event['start'][15]

        s_hour = int(s_hour)
        s_minute = int(s_minute)

        e_hour = event['end'][11] + event['end'][12]
        e_minute = event['end'][14] + event['end'][15]
        e_hour = int(e_hour)
        e_minute = int(e_minute)

        event_string = "%s -> %02d:%02d - %02d:%02d"%(day, s_hour, s_minute, e_hour, e_minute)
        readable_list.append(event_string)

    # Adds meeting to model
    project.meetings = event_list
    project.save()

    project.readable_meetings = json.dumps(readable_list)
    project.save()

    return "Something"
