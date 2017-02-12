from django.shortcuts import render
from .models import *
from .forms import *

# Create your views here.

def home(request):
    return render(request, 'core/home.html')

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

def view_projects(request):
    return render(request, 'core/view_projects.html')
