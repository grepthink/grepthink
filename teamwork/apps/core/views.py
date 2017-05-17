"""
Core views provide main site functionality.

"""
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from teamwork.apps.courses.models import *
from teamwork.apps.projects.models import *

from .forms import *
from .models import *


def login_view(request):
    page_name = "Login"
    page_description = ""
    title = "Login"
    if request.user.is_authenticated():
        # TODO: get feed of project updates (or public projects) to display on login
        return render(request, 'courses/view_course.html', {'page_name': page_name,
            'page_description': page_description, 'title' : title})
    else:
        # Redirect user to login instead of public index (for ease of use)
        return render(request, 'core/login.html', {'page_name': page_name,
            'page_description': page_description, 'title' : title})

def index(request):
    """
    The main index of Teamwork, referred to as "Home" in the sidebar.
    Accessible to public and logged in users.
    """
    # TODO: get feed of project updates (or public projects) to display on login

    # Populate with defaults for not logged in user
    page_name = "GrepThink"
    page_description = "Build Better Teams"
    title = "Welcome"
    date_updates = None
    logged_in = request.user.is_authenticated();

    if not logged_in:
        return render(request, 'core/landing.html', {'page_name' : page_name,
            'page_description' : page_description, 'title' : title})

    if logged_in:
        page_name = "Timeline"
        page_description = "Recent Updates from Courses and Projects"
        title = "Timeline"
        all_courses = Course.get_my_courses(request.user)
        date_updates = []
        for course in all_courses:
            date_updates.extend(course.get_updates_by_date())

    return render(request, 'core/index.html', {'page_name' : page_name,
         'page_description' : page_description, 'title' : title,
         'date_updates' : date_updates, 'logged_in' : logged_in})

def about(request):
    page_name = "About"
    page_description = "About"
    title = "About"
    return render(request, 'core/about.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title})

@login_required
def view_matches(request):
    """
    Generic view for serving a list of projects and potential teammate matches for
        each project.
    """
    project_match_list = []
    course_set = []

    page_name = "View Matches"
    page_description = "View Matching Students"
    title = "View Matches"

    if request.user.profile.isProf:
        courses = Course.get_my_created_courses(request.user)
        for course in courses:
            for project in course.projects.all():
                p_match = po_match(project)
                project_match_list.extend([(course, project, p_match)])
            course_set.append(course)
    else:
        my_projects = Project.get_my_projects(request.user)
        my_created = Project.get_created_projects(request.user)
        projects = my_projects | my_created
        projects = list(set(projects))
        for project in projects:
            p_match = po_match(project)
            project_match_list.extend([(project, p_match)])

    return render(request, 'core/view_matches.html', {
        'project_match_list' : project_match_list, 'course_set': course_set, 'page_name': page_name,
            'page_description': page_description, 'title' : title})


def auto_gen(request, slug):
    """
    Generic view for serving a list of projects and potential teammate matches for
        each project.
    """
    page_name = "Potential Roster"
    page_description = "Auto Generate Groups"
    title = "Auto Generate Groupts"
    
    course = get_object_or_404(Course, slug=slug)
    project_match_list = []

    auto = auto_ros(course)

    # Get just the projects so partial_project_box.html can loop through easily.
    # Will have to changes this once we get a better ui for autogen.
    projects = [x[0] for x in auto]


    return render(request, 'core/auto_gen.html', {
        'auto_gen' : auto, 'course': course, 'projects':projects, 'page_name': page_name,
            'page_description': page_description, 'title' : title})
