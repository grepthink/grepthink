from .models import *
from .forms import *

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

def _courses(request, courses):
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
    return render(request, 'courses/view_courses.html', {
        'courses': courses, 
    })

def view_courses(request):
    """
    Public method that takes a request, retrieves all Project objects from the model, 
    then calls _projects to render the request to template view_projects.html
    """
    all_courses = Course.get_published()
    return _courses(request, all_courses)

def create_course(request):
    """
    Public method that creates a form and renders the request to create_project.html
    """
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            # create an object for the input
            course = Course()
            course.name = form.cleaned_data.get('Name')
            course.students = form.cleaned_data.get('Students')
            # save this object
            course.save()
            # loop through the members in the object and make m2m rows for them
            for i in course.students:
                Enrollment.objects.create(user=i, course=course)
            # we dont have to save again because we do not touch the project object
            # we are doing behind the scenes stuff (waves hand)
            return redirect('/view_courses.html/')
    else:
        form = CourseForm()
    return render(request, 'courses/create_course.html', {'form': form})
