from django.shortcuts import render
from .models import Course
from .forms import CourseForm

# Create your views here.

def home(request):
    return render(request, 'core/home.html')

def create_project(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
    else:
        form = CourseForm()
    return render(request, 'core/create_project.html', {'form': form})
