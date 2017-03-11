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


    projects = projects_in_course(slug)

    return render(request, 'courses/view_course.html', {
        'cur_course': cur_course , 'projects': projects
        })

def projects_in_course(slug):
    """
    Public method that takes a coursename, retreives the course object, returns
    a list of project objects
    """
    # Gets current course
    cur_course = Course.objects.get(slug=slug)
    projects = Project.objects.filter(course=cur_course)
    return projects

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
def show_interest(request, slug):
    user = request.user
    # current course
    cur_course = get_object_or_404(Course, slug=slug)
    # projects in current course
    projects = projects_in_course(slug)
    # enrollment objects containing current user
    enroll = Enrollment.objects.filter(user=request.user)
    # current courses user is in
    user_courses = Course.objects.filter(enrollment__in=enroll)

    # if current course not in users enrolled courses
    if not cur_course in user_courses and course.creator != user.username:
            messages.info(request,'You are not enrolled in this course')
            return HttpResponseRedirect('/course')
    #if not enough projects or user is not professor
    if user.profile.isProf:
        #redirect them with a message
        messages.info(request,'Professor cannot show interest')
        return HttpResponseRedirect('/course')
    #if not enough projects or user is not professor
    if len(projects) == 0:
        #redirect them with a message
        messages.info(request,'No projects to show interest in!')
        return HttpResponseRedirect('/course')


    # SHOULD ALSO HAVE CHECK TO SEE IF USER ALREADY HAS SHOWN INTEREST

    if request.method == 'POST':
        form = ShowInterestForm(request.user.id, request.POST, slug = slug)
        if form.is_valid():
            data=form.cleaned_data
            #Gets first choice, creates interest object for it

            if len(projects) >= 1:
                choice_1 = data.get('projects')
                choice_1.interest.add(Interest.objects.create(user=user, interest=5, interest_reason=''))
                choice_1.save()

            #Gets second choice, creates interest object for it
            if len(projects) >= 2:
                choice_2 = data.get('projects2')
                choice_2.interest.add(Interest.objects.create(user=user, interest=4, interest_reason=''))
                choice_2.save()

            #Gets third choice, creates interest object for it
            if len(projects) >= 3:
                choice_3 = data.get('projects3')
                choice_3.interest.add(Interest.objects.create(user=user, interest=3, interest_reason=''))
                choice_3.save()

            #Gets fourth choice, creates interest object for it
            if len(projects) >= 4:
                choice_4 = data.get('projects4')
                choice_4.interest.add(Interest.objects.create(user=user, interest=2, interest_reason=''))
                choice_4.save()

            #Gets fifth choice, creates interest object for it
            if len(projects) >= 5:
                choice_5 = data.get('projects5')
                choice_5.interest.add(Interest.objects.create(user=user, interest=1, interest_reason=''))
                choice_5.save()


            return redirect(view_one_course, slug)

    else:
        form = ShowInterestForm(request.user.id, slug = slug)


    return render(
            request, 'courses/show_interest.html',
            {'form': form,'cur_course': cur_course}
            )

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
            course.limit_creation = data.get('limit_creation')

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
