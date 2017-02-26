from .models import *
from .forms import *

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

# Create your views here.

#def home(request):
#    return render(request, 'core/home.html')

#Shouldnt have a use as of 2/11
"""
def create_course(request):
    #If post request we need to process form data
    if request.method == 'POST':
        #Create form instance and populate it with data from request
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
    #if a get we'll create a blank form
    else:
        form = CourseForm()
        #form.save()
    return render(request, 'core/create_project.html', {'form': form})
"""
"""
#Does not create a project because we dont know how to use many-to-many
def create_project(request):
    #If post request we need to process form data
    if request.method == 'POST':
        #Create form instance and populate it with data from request
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
    #if a get we'll create a blank form
    else:
        form = ProjectForm()
        #form.save()
    return render(request, 'core/create_project.html', {'form': form})

#this does not work as intended, result is listed as a QUERYSET
def view_projects(request):
    project_name = Project.objects.all()
    context = { 'project_name': project_name,
    }
    return render(request, 'core/view_projects.html', context)

"""

def _projects(request, projects):
    """
    Private method that will be used for paginator once I figure out how to get it working.
    """
    #paginator = Paginator(projects, 10)
    page = request.GET.get('page')
    #try:
    #    projects = paginator.page(page)
    #except PageNotAnInteger:
    #    projects = paginator.page(1)
    #except EmptyPage:
    #    projects = paginator.page(paginator.num_pages)
    return render(request, 'projects/view_projects.html', {
        'projects': projects,
    })

@login_required
def view_projects(request):
    """
    Public method that takes a request, retrieves all Project objects from the model,
    then calls _projects to render the request to template view_projects.html
    """
    all_projects = Project.get_published()
    return _projects(request, all_projects)

@login_required
def create_project(request):
    """
    Public method that creates a form and renders the request to create_project.html
    """
    if request.method == 'POST':
        form = ProjectForm(request.user.id, request.POST)
        if form.is_valid():
            # create an object for the input
            project = Project()
            project.title = form.cleaned_data.get('title')
            # project.member = form.cleaned_data.get('members')
            members = form.cleaned_data.get('members')
            print(len(members))
            project.creator = request.user.username
            # save this object
            project.avail_mem = form.cleaned_data.get('accepting')
            
            project.save()
            # loop through the members in the object and make m2m rows for them
            for i in members:
                Membership.objects.create(user=i, project=project, invite_reason='')
            # we dont have to save again because we do not touch the project object
            # we are doing behind the scenes stuff (waves hand)
            return redirect('/view_projects.html/')
    else:
        form = ProjectForm(request.user.id)
    return render(request, 'projects/create_project.html', {'form': form})
