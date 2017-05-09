# import of other files in app
from .models import *
from .forms import *

from teamwork.apps.projects.models import *

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
    course = get_object_or_404(Course, slug=slug)
    projects = projects_in_course(slug)
    date_updates = course.get_updates_by_date()

    return render(request, 'courses/view_course.html', {
        'course': course , 'projects': projects, 'date_updates': date_updates
        })


@login_required
def view_stats(request, slug):
    cur_course = get_object_or_404(Course, slug=slug)

    if not request.user.profile.isProf:
        return redirect(view_one_course, cur_course.slug)

    students_num = Enrollment.objects.filter(course = cur_course)
    projects_num = projects_in_course(slug)
    students_projects = []
    students_projects_not = []
    emails = []
    cleanup_students = []
    cleanup_projects = []

    for i in projects_num:
        for j in i.members.all():
            if not j in students_projects:
                students_projects.append(j)

    for i in students_num:
        if not i.user in students_projects:
            students_projects_not.append(i.user)

    for i in students_num:
        if not i.user in cleanup_students:
            cleanup_students.append(i.user)

    for i in projects_num:
        if not i in cleanup_projects:
            cleanup_projects.append(i)

    for i in students_num:
        emails.append(i.user.email)

    num_in = len(students_projects)
    num_not = len(students_projects_not)
    num_total = len(students_num)
    num_projects = len(projects_num)

    return render(request, 'courses/view_statistics.html', {
        'cur_course': cur_course, 'students_num': students_num,
        'cleanup_students': cleanup_students, 'projects_num': projects_num,
        'cleanup_projects': cleanup_projects, 'students_projects': students_projects,
        'students_projects_not': students_projects_not, 'emails': emails,
        'num_in': num_in, 'num_not': num_not, 'num_total': num_total,
        'num_projects': num_projects
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
                    return redirect(view_one_course, i.slug)

            #returns to view courses
            return redirect(view_courses)
    else:
        form = JoinCourseForm(request.user.id)
    return render(request, 'courses/join_course.html', {'form': form})

@login_required
def show_interest(request, slug):
    """
    public method that takes in a slug and generates a form for the user
    to show interest in all projects in a given course
    """
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

            # Clear all interest objects where user is current user and for this course, avoid duplicates
            all_interests = Interest.objects.filter(project__in=projects)
            interests = all_interests.filter(user=user)
            if interests is not None: interests.delete()

            if len(projects) >= 1:
                choice_1 = data.get('projects')
                r1 = data.get('p1r')
                choice_1.interest.add(Interest.objects.create(user=user, interest=5, interest_reason=r1))
                choice_1.save()

            #Gets second choice, creates interest object for it
            if len(projects) >= 2:
                choice_2 = data.get('projects2')
                r2 = data.get('p2r')
                choice_2.interest.add(Interest.objects.create(user=user, interest=4, interest_reason=r2))
                choice_2.save()

            #Gets third choice, creates interest object for it
            if len(projects) >= 3:
                choice_3 = data.get('projects3')
                r3 = data.get('p3r')
                choice_3.interest.add(Interest.objects.create(user=user, interest=3, interest_reason=r3))
                choice_3.save()

            #Gets fourth choice, creates interest object for it
            if len(projects) >= 4:
                choice_4 = data.get('projects4')
                r4 = data.get('p4r')
                choice_4.interest.add(Interest.objects.create(user=user, interest=2, interest_reason=r4))
                choice_4.save()

            #Gets fifth choice, creates interest object for it
            if len(projects) >= 5:
                choice_5 = data.get('projects5')
                r5 = data.get('p5r')
                choice_5.interest.add(Interest.objects.create(user=user, interest=1, interest_reason=r5))
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
            course.limit_weights = data.get('limit_weights')
            course.weigh_interest = data.get('weigh_interest') or 0
            course.weigh_know = data.get('weigh_know') or 0
            course.weigh_learn = data.get('weigh_learn') or 0


            # creator is current user
            course.creator = request.user.username
            students = data.get('students')
            # save this object
            course.save()
            # loop through the members in the object and make m2m rows for them
            for i in students:
                Enrollment.objects.create(user=i.user, course=course)
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
            course.limit_creation = data.get('limit_creation')
            students = data.get('students')
            course.limit_weights = data.get('limit_weights')
            course.weigh_interest = data.get('weigh_interest') or 0
            course.weigh_know = data.get('weigh_know') or 0
            course.weigh_learn = data.get('weigh_learn') or 0


            course.save()
            # clear all enrollments
            enrollments = Enrollment.objects.filter(course=course)
            if enrollments is not None: enrollments.delete()
            for i in students:
                Enrollment.objects.create(user=i.user, course=course)

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

@login_required
def update_course(request, slug):
    """
    Post an update for a given course
    """
    course = get_object_or_404(Course, slug=slug)

    if request.method == 'POST':
        form = CourseUpdateForm(request.user.id, request.POST)
        if form.is_valid():
            new_update = CourseUpdate(course=course)
            new_update.course = course;
            new_update.title = form.cleaned_data.get('title')
            new_update.content = form.cleaned_data.get('content')
            new_update.creator = request.user
            new_update.save()
            return redirect(view_one_course, course.slug)
    else:
        form = CourseUpdateForm(request.user.id)

    return render(
            request, 'courses/update_course.html',
            {'form': form, 'course': course}
            )


@login_required
def update_course_update(request, slug, id):
    """
    Edit an update for a given course
    """
    course = get_object_or_404(Course, slug=slug)
    update = get_object_or_404(CourseUpdate, id=id)

    if update.creator != request.user:
        return redirect(view_one_course, course.slug)
    elif request.method == 'POST':
        form = CourseUpdateForm(request.user.id, request.POST)
        if form.is_valid():
            update.course = course;
            update.title = form.cleaned_data.get('title')
            update.content = form.cleaned_data.get('content')
            update.creator = request.user
            update.save()
            return redirect(view_one_course, course.slug)
    else:
        form = CourseUpdateForm(request.user.id, instance=update)

    return render(
            request, 'courses/update_course_update.html',
            {'form': form, 'course': course, 'update': update}
            )


@login_required
def delete_course_update(request, slug, id):
    """
    Delete an update for a given course
    """
    course = get_object_or_404(Course, slug=slug)
    update = get_object_or_404(CourseUpdate, id=id)

    if update.creator == request.user:
        update.delete()

    return redirect(view_one_course, course.slug)
