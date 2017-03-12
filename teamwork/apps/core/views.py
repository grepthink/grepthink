"""
Core views provide main site functionality.

"""
from .models import *
from .forms import *

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from teamwork.apps.projects.models import *

def login_view(request):
    if request.user.is_authenticated():
        # TODO: get feed of project updates (or public projects) to display on login
        return render(request, 'courses/view_course.html')
    else:
        # Redirect user to login instead of public index (for ease of use)
        return render(request, 'core/login.html')

def index(request):
    # TODO: get feed of project updates (or public projects) to display on login
    # if request.user.is_authenticated():
    return render(request, 'core/index.html')

def about(request):
    return render(request, 'core/about.html')

@login_required
def view_matches(request):
    """
    Generic view for serving a list of projects and potential teammate matches for 
        each project.
    """
    project_match_list = []

    projects = Project.get_my_projects(request.user)

    print("PROJECTS:")
    print(projects)
    
    for project in projects:
        print("Project:")
        print(project)
        p_match = po_match(project)
        print("p_match:")
        print(p_match)
        project_match_list.extend([(project, p_match)])

    print("Project Match List:")
    print(project_match_list)

    for project in project_match_list:
        print("project in project_match_list")
        print(project)
        print(project[0].title)
        print(project[1][0].username)

    return render(request, 'core/view_matches.html', {
        'project_match_list' : project_match_list
        })