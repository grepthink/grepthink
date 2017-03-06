# import of other files in app
from .models import *
from .forms import *

# Django Imports
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

def _courses(request, courses):
    """
    Private method that will be used for paginator once I figure out how to get it working.
    """
    page = request.GET.get('page')

    return render(request,
            'courses/view_courses.html',
            {'courses': courses,}
            )

@login_required
def view_courses(request):
    """
    Public method that takes a request, retrieves certain course objects from the model,
    then calls _projects to render the request to template view_projects.html
    """

    #If user is a professor, they can see all courses they have created
    if request.user.profile.isProf:
        all_courses=Course.get_my_created_courses(request.user)
    #else returns a list of courses the user is enrolled in
    else:
        all_courses = Course.get_my_courses(request.user)
    return _courses(request, all_courses)

@login_required
def view_one_course(request, slug):
    """
    Public method that takes a request and a coursename, retrieves the Course object from the model
    with given coursename.  Renders courses/view_course.html
    """
    cur_course = get_object_or_404(Course, slug=slug)

    return render(request, 'courses/view_course.html', {
        'cur_course': cur_course ,
        })


@login_required
def join_course(request):
    """
    Public method that takes a request, renders form that enables a user
    to add a course, renders in join_course.html
    """
    if request.method == 'POST':
        # send the current user.id to filter out
        form = JoinCourseForm(request.user.id,request.POST)
        #if form is accepted
        if form.is_valid():
            #the courseID will be gotten from the form
            data = form.cleaned_data
            course_code = data.get('code')
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
            return redirect(view_courses)
    else:
        form = JoinCourseForm(request.user.id)
    return render(request, 'courses/join_course.html', {'form': form})

@login_required
def create_course(request):
    """
    Public method that creates a form and renders the request to create_course.html
    """
    #If user is not a professor
    if not request.user.profile.isProf:
        #redirect them to the /course directory
        messages.info(request,'Only Professor can create course!')
        return HttpResponseRedirect('/course')
    #If request is POST
    if request.method == 'POST':
        # send the current user.id to filter out
        form = CourseForm(request.user.id,request.POST)
        if form.is_valid():
            # create an object for the input
            course = Course()
            # gets data from form
            data = form.cleaned_data
            course.name = data.get('name')
            course.info = data.get('info')
            course.term = data.get('term')
            course.slug = data.get('slug')
            course.professor = data.get('professor')

            # creator is current user
            course.creator = request.user.username
            students = data.get('students')
            # save this object
            course.save()
            # loop through the members in the object and make m2m rows for them
            for i in students:
                Enrollment.objects.create(user=i, course=course)
            # we dont have to save again because we do not touch the project object
            # we are doing behind the scenes stuff (waves hand)
            return redirect(view_one_course, course.slug)
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

    #if user is not a professor or they did not create course
    if not request.user.profile.isProf or not course.creator == request.user.username:
        #redirect them to the /course directory with message
        messages.info(request,'Only Professor can edit course')
        return HttpResponseRedirect('/course')

    if request.method == 'POST':

        # send the current user.id to filter out
        form = CourseForm(request.user.id,request.POST)
        if form.is_valid():
            # edit the course object, omitting slug
            data = form.cleaned_data
            course.name = data.get('name')
            course.info = data.get('info')
            course.term = data.get('term')
            students = data.get('students')
            course.save()
            # clear all enrollments
            enrollments = Enrollment.objects.filter(course=course)
            if enrollments is not None: enrollments.delete()
            for i in students:
                Enrollment.objects.create(user=i, course=course)

        return redirect(view_one_course, course.slug)
    else:
        form = CourseForm(request.user.id, instance=course)
    return render(
            request, 'courses/edit_course.html',
            {'form': form,'course': course}
            )


@login_required
def delete_course(request, slug):
    """
    Delete course method
    """
    course = get_object_or_404(Course, slug=slug)
    if not request.user.profile.isProf:
        return redirect(view_one_course, course.slug)
    else:
        course.delete()
        return redirect(view_courses)
