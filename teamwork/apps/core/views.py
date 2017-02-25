from .models import *
from .forms import *

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    if request.user.is_authenticated():
        return render(request, 'core/home.html')
    else:
        return render(request, 'core/cover.html')



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

