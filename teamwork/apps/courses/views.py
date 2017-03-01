from .models import *
from .forms import *

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

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

@login_required
def view_courses(request):
    """
    Public method that takes a request, retrieves all Project objects from the model,
    then calls _projects to render the request to template view_projects.html
    """
    all_courses = Course.get_published()
    return _courses(request, all_courses)

@login_required
def view_one_course(request, slug):
    """
    Public method that takes a request and a coursename, retrieves the Course object from the model
    with given coursename.  Renders courses/view_course.html

    TODO:

    """
    cur_course = get_object_or_404(Course, slug=slug)

    return render(request, 'courses/view_course.html', {
        'cur_course': cur_course ,
        })


@login_required
def join_course(request):
    """
    Public method that takes a request,
    """
    if request.method == 'POST':
        # send the current user.id to filter out
        form = JoinCourseForm(request.user.id,request.POST)
        #if form is accepted
        if form.is_valid():
            #the courseID will be gotten from the form
            course_code = form.cleaned_data.get('code')
            all_courses = Course.objects.all()
            #loops through the courses to find the course with corresponding course_code
            # O(n) time
            for i in all_courses:
                if course_code == i.addCode:
                    #checks to see if an enrollment already exists
                    if not Enrollment.objects.filter(user=request.user, course=i).exists():
                        #creates an enrollment relation with the current user and the selected course
                        Enrollment.objects.create(user=request.user, course=i)
            #returns to view courses
            return redirect('/view_courses.html/')
    else:
        form = JoinCourseForm(request.user.id)
    return render(request, 'courses/join_course.html', {'form': form})

@login_required
def create_course(request):
    """
    Public method that creates a form and renders the request to create_project.html
    """
    if request.method == 'POST':
        # send the current user.id to filter out
        form = CourseForm(request.user.id,request.POST)
        if form.is_valid():
            # create an object for the input
            course = Course()
            course.name = form.cleaned_data.get('name')
            course.info = form.cleaned_data.get('info')
            course.term = form.cleaned_data.get('term')
            course.slug = form.cleaned_data.get('slug')

            course.creator = request.user.username
            students = form.cleaned_data.get('students')
            # save this object
            course.save()
            # loop through the members in the object and make m2m rows for them
            for i in students:
                Enrollment.objects.create(user=i, course=course)
            # we dont have to save again because we do not touch the project object
            # we are doing behind the scenes stuff (waves hand)
            return redirect('/course')
    else:
        form = CourseForm(request.user.id)
    return render(request, 'courses/create_course.html', {'form': form})

@login_required
def edit_course(request, slug):
    """
    Edit course method, creating generic form
    https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-editing/
    """
    course = get_object_or_404(Course, slug=slug)

    if request.method == 'POST':
        # TODO: figure out a better way to do this
        if "DELETE" in request.POST:
            course.delete()
        else:
            # send the current user.id to filter out
            form = CourseForm(request.user.id,request.POST)
            if form.is_valid():
                # edit the course object, omitting slug
                course.name = form.cleaned_data.get('name')
                course.info = form.cleaned_data.get('info')
                course.term = form.cleaned_data.get('term')
                students = form.cleaned_data.get('students')
                course.save()
                # clear all enrollments
                enrollments = Enrollment.objects.filter(course=course)
                if enrollments is not None: enrollments.delete()
                for i in students:
                    Enrollment.objects.create(user=i, course=course)
        return redirect('/course')
    else:
        form = CourseForm(request.user.id, instance=course)
    return render(request, 'courses/edit_course.html', {'form': form,
        'course': course})

