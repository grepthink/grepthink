from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from teamwork.apps.projects.models import Project
from teamwork.apps.projects.forms import *

@login_required
def view_projects(request):
    """
    Public method that takes a request, retrieves all Project objects from the model,
    then calls _projects to render the request to template view_projects.html
    """
    active_projects = Project.get_my_active_projects(request.user)
    inactive_projects = Project.get_my_disabled_projects(request.user)

    return _projects(request, active_projects, inactive_projects )

def _projects(request, active, inactive):
    """
    Private method that will be used for paginator once I figure out how to get it working.
    """
    page = request.GET.get('page')

    # Populate with page name and title
    page_name = "My Projects"
    page_description = "Projects created by " + request.user.username
    title = "My Projects"

    return render(request, 'projects/view_projects.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title,
        'active': active, 'inactive': inactive})

def techs(request):
    return render(request, 'projects/view_projects.html',{}) 
