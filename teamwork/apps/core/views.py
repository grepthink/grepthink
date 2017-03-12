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

def home(request):
    if request.user.is_authenticated():
        return render(request, 'core/home.html')
    else:
        return render(request, 'core/about.html')

def about(request):
    return render(request, 'core/about.html')

@login_required
def view_matches(request):
    """
    Generic view for serving a list of projects and potential teammate matches for 
        each project.
    """
    project_match_dict = {}

    projects = Project.get_my_projects(request.user)
    
    for project in projects:
        p_match = po_match(project)
        project_match_dict[project.slug] = (project, p_match)

    return render(request, 'core/view_matches.html', {
        'project_match_dict' : project_match_dict
        })