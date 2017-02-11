from django.shortcuts import render
from .models import Course

# Create your views here.

def home(request):
    return render(request, 'core/home.html')

def create_project(request):
    return render(request, 'core/create_project.html')
