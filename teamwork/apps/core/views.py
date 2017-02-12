from django.shortcuts import render
from .models import Course
from .forms import CourseForm

# Create your views here.

def home(request):
    return render(request, 'core/home.html')

def create_project(request):
    #If post request we need to process form data
    if request.method == 'POST':
        #Create form instance and populate it with data from request
        form = CourseForm(request.POST)
        form.save()
    #if a get we'll create a blank form
    else:
        form = CourseForm()
        form.save()
    return render(request, 'core/create_project.html', {'form': form})
