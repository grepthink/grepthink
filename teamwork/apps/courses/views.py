# import of other files in app
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Django Imports
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, redirect, render

from django.urls import reverse

from django.contrib import messages

from teamwork.apps.projects.models import *
from teamwork.apps.core.helpers import *
from teamwork.apps.core.forms import *
from .forms import *
from .models import *

from datetime import datetime

import csv
import codecs

from datetime import datetime


def _courses(request, courses):
    """
    Private method that will be used for paginator once I figure out how to get it working.
    """
    page = request.GET.get('page')
    page_name = "Courses"
    page_description = "Course List"
    title = "Courses"

    return render(request,
                  'courses/view_courses.html',
                  {'courses': courses, 'page_name': page_name, 'page_description': page_description, 'title': title}
                  )


@login_required
def view_courses(request):
    """
    Public method that takes a request, retrieves certain course objects from the model,
    then calls _projects to render the request to template view_projects.html
    """

    # Show all courses to a GT account
    if request.user.profile.isGT:
        all_courses = get_all_courses(request)
    # If user is a professor, they can see all courses they have created
    elif request.user.profile.isProf:
        all_courses = Course.get_my_created_courses(request.user)
    # else returns a list of courses the user is enrolled in
    else:
        all_courses = Course.get_my_courses(request.user)

    # Returns all courses
    return _courses(request, all_courses)


@login_required
def view_one_course(request, slug):
    """
    Public method that takes a request and a coursename, retrieves the Course object from the model
    with given coursename.  Renders courses/view_course.html
    """
    course = get_object_or_404(Course, slug=slug)
    page_name = "%s" % (course.name)
    page_description = "Course Overview"
    title = "%s" % (slug)

    if not request.user.profile.isGT:
        # check if current user is enrolled in the course
        if request.user in course.students.all() or (request.user == course.creator):
            user_role = Enrollment.objects.filter(user=request.user, course=course).first().role
        else:
            # init user_role otherwise
            user_role = "not enrolled"
    else:
        user_role = 'GT'

    # TODO: get rid of isProf and use user_role
    if request.user == course.creator:
        isProf = 1
    else:
        isProf = 0

    projects = projects_in_course(slug)
    projectCount = len(projects)
    # sort the list of projects alphabetical, but not case sensitive (aka by ASCII)
    projects = sorted(projects, key=lambda s: s.title.lower())
    date_updates = course.get_updates_by_date()
    profile = Profile.objects.get(user=request.user)
    students = Enrollment.objects.filter(course=course, role="student")
    staff = course.get_staff()
    asgs = list(course.assignments.all())

    available = []
    for i in students:
        available.append(i.user)

    for i in projects:
        for j in i.members.all():
            if j in available:
                available.remove(j)

    student_users = []
    for stud in students:
        temp_user = get_object_or_404(User, username=stud)
        student_users.append(temp_user)

    assignmentForm = AssignmentForm(request.user.id, slug)
    if (request.method == 'POST'):
        assignmentForm = AssignmentForm(request.user.id, slug, request.POST)
        if assignmentForm.is_valid():
            ass = Assignment()
            ass.due_date = assignmentForm.cleaned_data.get('due_date')
            ass.ass_date = assignmentForm.cleaned_data.get('ass_date')
            ass.ass_type = assignmentForm.cleaned_data.get('ass_type').lower()
            ass.ass_name = assignmentForm.cleaned_data.get('ass_name')
            ass.description = assignmentForm.cleaned_data.get('description')
            ass.ass_number = assignmentForm.cleaned_data.get('ass_number')
            print(ass.ass_number)

            ass.save()

            course.assignments.add(ass)
            course.save()

        messages.info(request, 'You have successfully created an assignment')
        return redirect(view_one_course, course.slug)

    return render(request, 'courses/view_course.html', {'isProf': isProf, 'assignmentForm': assignmentForm,
                                                        'course': course, 'projects': projects,
                                                        'date_updates': date_updates, 'students': student_users,
                                                        'user_role': user_role, 'available': available,
                                                        'assignments': asgs, 'projectCount': projectCount,
                                                        'page_name': page_name, 'page_description': page_description,
                                                        'title': title, 'staff': staff})


@login_required
def view_stats(request, slug):
    cur_course = get_object_or_404(Course, slug=slug)
    page_name = "Statistics"
    page_description = "Statistics for %s" % (cur_course.name)
    title = "Statistics"

    if not request.user.profile.isGT:
        user_role = Enrollment.objects.filter(user=request.user, course=cur_course).first().role
    else:
        user_role = 'GT'

    if request.user.profile.isGT:
        pass
    elif not request.user == cur_course.creator:
        if not user_role == "ta":
            return redirect(view_one_course, cur_course.slug)

    students_num = Enrollment.objects.filter(course=cur_course, role="student")
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
        'page_name': page_name, 'page_description': page_description, 'title': title,
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
    projects = Project.objects.filter(course=cur_course).order_by('-tagline')
    return projects


@login_required
def join_course(request):
    """
    Public method that takes a request, renders form that enables a user
    to add a course, renders in join_course.html
    """

    page_name = "Join Course"
    page_description = "Join a Course!"
    title = "Join Course"

    if request.user.profile.isProf:
        role = 'professor'
    else:
        role = 'student'

    if request.method == 'POST':
        # send the current user.id to filter out
        form = JoinCourseForm(request.user.id, request.POST)
        # if form is accepted
        if form.is_valid():
            # the courseID will be gotten from the form
            data = form.cleaned_data
            course_code = data.get('code')
            all_courses = Course.objects.all()
            # loops through the courses to find the course with corresponding course_code
            # O(n) time
            for i in all_courses:
                if course_code == i.addCode:
                    # checks to see if an enrollment already exists
                    if not Enrollment.objects.filter(user=request.user, course=i, role=role).exists():
                        # creates an enrollment relation with the current user and the selected course
                        Enrollment.objects.create(user=request.user, course=i, role=role)
                        Alert.objects.create(
                            sender=request.user,
                            to=i.creator,
                            msg=request.user.username + " used the addcode to enroll in " + i.name,
                            url=reverse('profile', args=[request.user.username]),
                        )
                    return redirect(view_one_course, i.slug)

            # returns to view courses
            return redirect(view_courses)
    else:
        form = JoinCourseForm(request.user.id)
    return render(request, 'courses/join_course.html',
                  {'form': form, 'page_name': page_name, 'page_description': page_description, 'title': title})


# @login_required
# def drop_course(request, slug):
#     #Does not delete projects
#     user = request.user
#     # current course
#     cur_course = get_object_or_404(Course, slug=slug)
#     # projects in current course
#     projects = projects_in_course(slug)
#     # enrollment objects containing current user
#     user_courses = request.user.enrollment.all()
#     # current courses user is in
#     to_delete = Enrollment.objects.filter(user=user, course=cur_course, role="student")
#
#     for mem_obj in to_delete:
#         Alert.objects.create(
#             sender=request.user,
#             to=f_user,
#             msg="You were removed from: " + course.name,
#             url=reverse('view_one_course',args=[course.slug]),
#             )
#         mem_obj.delete()
#         removed = True
#
#     if removed:
#         messages.add_message(request, messages.SUCCESS, "Member(s) successfully removed from the course.")
#     else:
#         messages.add_message(request, messages.SUCCESS, "Failed to succesfully remove member(s) from the course.")
#
#     return HttpResponseRedirect('/course')

@login_required
def edit_interest(request, slug):
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
    user_courses = request.user.enrollment.all()
    # current courses user is in
    # user_courses = Course.objects.filter(enrollment__in=enroll)

    page_name = "Show Interest"
    page_description = "Show Interest in Projects for %s" % (cur_course.name)
    title = "Show Interest"

    # if user is professor
    if user.profile.isProf:
        # redirect them with a message
        messages.info(request, 'Professor cannot show interest')
        return HttpResponseRedirect('/course')

    # if not enough projects
    if len(projects) == 0:
        # redirect them with a message
        messages.info(request, 'No projects to show interest in!')
        return HttpResponseRedirect('/course')

    # if course has disabled setting interest
    if cur_course.limit_interest:
        # redirect them with a message
        messages.info(request, 'Can no longer show interest!')
        return HttpResponseRedirect('/course')

    # if current course not in users enrolled courses
    if not cur_course in user_courses and cur_course.creator != user:
        messages.info(request, 'You are not enrolled in this course')
        return HttpResponseRedirect('/course')

    # TODO: SHOULD ALSO HAVE CHECK TO SEE IF USER ALREADY HAS SHOWN INTEREST

    if request.method == 'POST':
        form = ShowInterestForm(request.user.id, request.POST, slug=slug)
        if form.is_valid():
            show_interest_course = Reasons()
            show_interest_course.reason1 = form.cleaned_data.get('p1r')
            r1 = show_interest_course.reason1
            r2 = show_interest_course.reason2
            r3 = show_interest_course.reason3

            if r1:
                show_interest_course.save()
                messages.info(request, r1)
            if r2:
                show_interest_course.save()
                messages.info(request, r2)


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
    user_courses = request.user.enrollment.all()
    # current courses user is in
    # user_courses = Course.objects.filter(enrollment__in=enroll)

    page_name = "Show Interest"
    page_description = "Show Interest in Projects for %s" % (cur_course.name)
    title = "Show Interest"

    # if user is professor
    if user.profile.isProf:
        # redirect them with a message
        messages.info(request, 'Professor cannot show interest')
        return HttpResponseRedirect('/course')

    # if not enough projects
    if len(projects) == 0:
        # redirect them with a message
        messages.info(request, 'No projects to show interest in!')
        return HttpResponseRedirect('/course')

    # if course has disabled setting interest
    if cur_course.limit_interest:
        # redirect them with a message
        messages.info(request, 'Can no longer show interest!')
        return HttpResponseRedirect('/course')

    # if current course not in users enrolled courses
    if not cur_course in user_courses and cur_course.creator != user:
        messages.info(request, 'You are not enrolled in this course')
        return HttpResponseRedirect('/course')

    # TODO: SHOULD ALSO HAVE CHECK TO SEE IF USER ALREADY HAS SHOWN INTEREST

    if request.method == 'POST':
        form = ShowInterestForm(request.user.id, request.POST, slug=slug)
        if form.is_valid():

            # Gets first choice, creates interest object for it

            # Clear all interest objects where user is current user and for this course, avoid duplicates
            all_interests = Interest.objects.filter(project_interest=projects)
            interests = user.interest.all()
            data = form.cleaned_data
            if interests is not None: interests.delete()

            if len(projects) >= 1:
                choice_1 = data.get('projects')
                r1 = data.get('p1r')
                choice_1.interest.add(Interest.objects.create(user=user, interest=5, interest_reason=r1))
                choice_1.save()

            # Gets second choice, creates interest object for it
            if len(projects) >= 2:
                choice_2 = data.get('projects2')
                r2 = data.get('p2r')
                choice_2.interest.add(Interest.objects.create(user=user, interest=4, interest_reason=r2))
                choice_2.save()

            # Gets third choice, creates interest object for it
            if len(projects) >= 3:
                choice_3 = data.get('projects3')
                r3 = data.get('p3r')
                choice_3.interest.add(Interest.objects.create(user=user, interest=3, interest_reason=r3))
                choice_3.save()

            # Gets fourth choice, creates interest object for it
            if len(projects) >= 4:
                choice_4 = data.get('projects4')
                r4 = data.get('p4r')
                choice_4.interest.add(Interest.objects.create(user=user, interest=2, interest_reason=r4))
                choice_4.save()

            # Gets fifth choice, creates interest object for it
            if len(projects) >= 5:
                choice_5 = data.get('projects5')
                r5 = data.get('p5r')
                choice_5.interest.add(Interest.objects.create(user=user, interest=1, interest_reason=r5))
                choice_5.save()

            messages.success(request, "You have left succesfully submitted interest")

            return redirect(view_one_course, slug)

    else:
        form = ShowInterestForm(request.user.id, slug=slug)

    return render(
        request, 'courses/show_interest.html',
        {'form': form, 'cur_course': cur_course, 'page_name': page_name, 'page_description': page_description,
         'title': title}
    )


@login_required
def create_course(request):
    """
    Public method that creates a form and renders the request to create_course.html
    """

    page_name = "Create Course"
    page_description = "Create a Course!"
    title = "Create Course"

    if request.user.profile.isGT:
        pass
    elif not request.user.profile.isProf:
        # redirect them to the /course directory
        messages.info(request, 'Only Professor can create course!')
        return HttpResponseRedirect('/course')

    # If request is POST
    if request.method == 'POST':
        # send the current user.id to filter out
        form = CreateCourseForm(request.user.id, request.POST, request.FILES)
        if form.is_valid():
            # create an object for the input
            course = Course()
            # gets data from form
            data = form.cleaned_data
            course.name = data.get('name')
            course.info = data.get('info')
            course.term = data.get('term')
            course.slug = data.get('slug')
            course.limit_creation = data.get('limit_creation')
            course.limit_weights = data.get('limit_weights')
            course.weigh_interest = data.get('weigh_interest') or 0
            course.weigh_know = data.get('weigh_know') or 0
            course.weigh_learn = data.get('weigh_learn') or 0

            # creator is current user
            course.creator = request.user
            students = data.get('students')
            # save this object
            course.save()

            # add enrollment object for professor
            if request.user.profile.isProf:
                Enrollment.objects.create(user=request.user, course=course, role="professor")

            return redirect(upload_csv, course.slug)
    else:
        form = CreateCourseForm(request.user.id)
    return render(request, 'courses/create_course.html',
                  {'form': form, 'page_name': page_name, 'page_description': page_description, 'title': title})


@login_required
def edit_course(request, slug):
    """
    Edit course method, creating generic form
    https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-editing/
    """
    course = get_object_or_404(Course, slug=slug)
    page_name = "Edit Course"
    page_description = "Edit %s" % (course.name)
    title = "Edit Course"

    tas = Enrollment.objects.filter(course=course, role="ta")
    students = Enrollment.objects.filter(course=course, role="student")

    if request.user.profile.isGT:
        userRole = 'GT'
    else:
        userRole = Enrollment.objects.filter(user=request.user, course=course).first().role

    if request.user.profile.isGT:
        pass
    # if user is not a professor or they did not create course
    elif not course.creator == request.user:
        # if user is not a TA
        if not user_role == "ta":
            # redirect them to the /course directory with message
            messages.info(request, 'Only Professor can edit course')
            return HttpResponseRedirect('/course')

    # Add a member to the course
    if request.POST.get('members'):
        # Get the members to add, as a list
        members = request.POST.getlist('members')
        enrollments = Enrollment.objects.filter(course=course)
        students = course.students.all()
        added = False

        # Create membership objects for the newly added members
        for uname in members:
            mem_to_add = User.objects.get(username=uname)
            mem_courses = Course.get_my_courses(mem_to_add)

            # Don't add a member if they already have membership in course
            # Confirm that the member is a part of the course
            # List comprehenshion: loops through this courses memberships in order
            #   to check if mem_to_add is in the user field of a current membership.
            if not course in mem_courses:
                if not mem_to_add in students:
                    Enrollment.objects.create(user=mem_to_add, course=course, role="student")
                    Alert.objects.create(
                        sender=request.user,
                        to=mem_to_add,
                        msg="You were added to: " + course.name,
                        url=reverse('view_one_course', args=[course.slug]),
                    )
                    added = True
        if added:
            messages.add_message(request, messages.SUCCESS, "Successfully added member(s) to course.")
        else:
            messages.add_message(request, messages.SUCCESS, "Failed to successfully add member(s) to course.")

        # return redirect(edit_course, slug)

    # Remove a user from the course
    if request.POST.get('remove_user'):
        members = request.POST.getlist('remove_user')
        removed = False

        for mem in members:
            f_user = User.objects.get(username=mem)
            to_delete = Enrollment.objects.filter(user=f_user, course=course, role="student")

            for mem_obj in to_delete:
                Alert.objects.create(
                    sender=request.user,
                    to=f_user,
                    msg="You were removed from: " + course.name,
                    url=reverse('view_one_course', args=[course.slug]),
                )
                mem_obj.delete()
                removed = True
        if removed:
            messages.add_message(request, messages.SUCCESS, "Member(s) successfully removed from the course.")
        else:
            messages.add_message(request, messages.SUCCESS, "Failed to succesfully remove member(s) from the course.")

        # return redirect(edit_course, slug)

    # Add a TA
    if request.POST.get('ta'):
        # Get the members to add, as a list
        members = request.POST.getlist('ta')
        enrollments = Enrollment.objects.filter(course=course)
        students = course.students.all()

        # Create membership objects for the newly added members
        for uname in members:
            mem_to_add = User.objects.get(username=uname)
            mem_courses = Course.get_my_courses(mem_to_add)

            # Don't add a member if they already have membership in course
            # Confirm that the member is a part of the course
            # List comprehenshion: loops through this courses memberships in order
            #   to check if mem_to_add is in the user field of a current membership.
            if mem_to_add in students:
                Enrollment.objects.filter(user=mem_to_add).update(role="ta")
            else:
                Enrollment.objects.create(user=mem_to_add, course=course, role="ta")
                Alert.objects.create(
                    sender=request.user,
                    to=mem_to_add,
                    msg="You were added to: " + course.name + " as a TA",
                    url=reverse('view_one_course', args=[course.slug]),
                )

        messages.add_message(request, messages.SUCCESS, "Successfully added TA to the course.")

        # return redirect(edit_course, slug)

    # Remove a ta from the course
    if request.POST.get('remove_ta'):
        f_username = request.POST.get('remove_ta')
        f_user = User.objects.get(username=f_username)
        to_delete = Enrollment.objects.filter(user=f_user, course=course, role="ta")

        for mem_obj in to_delete:
            Alert.objects.create(
                sender=request.user,
                to=f_user,
                msg="You were removed as the TA from: " + course.name,
                url=reverse('view_one_course', args=[course.slug]),
            )
            mem_obj.delete()

        messages.add_message(request, messages.SUCCESS, "Removed TA from Course.")

        # return redirect(edit_course, slug)

    if request.method == 'POST':
        # send the current user.id to filter out
        form = EditCourseForm(request.user.id, slug, request.POST, request.FILES)
        if form.is_valid():
            # edit the course object, omitting slug
            data = form.cleaned_data
            course.name = data.get('name')
            course.info = data.get('info')
            course.term = data.get('term')
            course.limit_creation = data.get('limit_creation')
            course.limit_weights = data.get('limit_weights')
            course.weigh_interest = data.get('weigh_interest') or 0
            course.weigh_know = data.get('weigh_know') or 0
            course.weigh_learn = data.get('weigh_learn') or 0
            course.limit_interest = data.get('limit_interest')
            course.save()
        else:
            print("FORM ERRORS: ", form.errors)

        return redirect(view_one_course, course.slug)
    else:
        form = EditCourseForm(request.user.id, slug, instance=course)

    return render(
        request, 'courses/edit_course.html',
        {'form': form, 'course': course, 'tas': tas, 'students': students, 'page_name': page_name,
         'page_description': page_description, 'title': title}
    )


@login_required
def edit_assignment(request, slug):
    """
    Edit assignment method, creating generic form
    """
    ass = get_object_or_404(Assignment, slug=slug)
    course = ass.course.first()
    page_name = "Edit Assignment"
    page_description = "Edit %s" % (ass.ass_name)
    title = "Edit Assignment"

    if not request.user.profile.isGT:
        user_role = Enrollment.objects.filter(user=request.user, course=course).first().role
    else:
        user_role = 'GT'

    if request.user.profile.isGT:
        pass
    # if user is not a professor or they did not create course
    elif not course.creator == request.user:
        if not user_role == "ta":
            # redirect them to the /course directory with message
            messages.info(request, 'Only a Professor or TA can Edit an Assignment')
            return HttpResponseRedirect('/course')

    if (request.method == 'POST'):
        assignmentForm = EditAssignmentForm(request.user.id, slug, request.POST)
        if assignmentForm.is_valid():
            data = assignmentForm.cleaned_data
            due_date = data.get('due_date')
            ass_date = data.get('ass_date')
            ass_type = data.get('ass_type').lower()
            ass_name = data.get('ass_name')
            description = data.get('description')
            ass_number = data.get('ass_number')

            # edit the current assignment's properties w/ the new values
            ass.due_date = due_date
            ass.ass_date = ass_date
            ass.ass_type = ass_type
            ass.ass_name = ass_name
            ass.description = description
            ass.ass_number = ass_number
            ass.save()
        else:
            print("FORM ERRORS: ", form.errors)

        return redirect(view_one_course, course.slug)

    else:
        form = EditAssignmentForm(request.user.id, slug, instance=ass)

    return render(
        request, 'courses/edit_assignment.html',
        {'assignmentForm': form, 'course': course, 'ass': ass, 'page_name': page_name,
         'page_description': page_description, 'title': title}
    )


@login_required
def delete_course(request, slug):
    """
    Delete course method
    """
    course = get_object_or_404(Course, slug=slug)
    projects = projects_in_course(slug)

    if request.user.profile.isGT:
        pass
    elif not request.user == course.creator:
        return redirect(view_one_course, course.slug)

    # Runs through each project and deletes them
    for p in projects:
        p.delete()

    # deletes course
    course.delete()
    return redirect(view_courses)


@login_required
def delete_assignment(request, slug):
    """
    Delete course method
    """
    ass = get_object_or_404(Assignment, slug=slug)
    course = ass.course.first()

    if not request.user.profile.isGT:
        user_role = Enrollment.objects.filter(user=request.user, course=course).first().role
    else:
        user_role = 'GT'

    print("user_role", user_role)

    if request.user.profile.isGT:
        pass
    elif not request.user == course.creator:
        if not user_role == "ta":
            return redirect(view_one_course, course.slug)

    # Runs through each project and deletes them
    for a in ass.subs.all():
        a.delete()

    # deletes course
    ass.delete()
    return redirect(view_one_course, course.slug)


@login_required
def update_course(request, slug):
    """
    Post an update for a given course
    """
    course = get_object_or_404(Course, slug=slug)
    page_name = "Update Course"
    page_description = "Update %s" % (course.name) or "Post a new update"
    title = "Update Course"

    if request.user.profile.isGT:
        pass
    # if user is not a professor or they did not create course
    elif not course.creator == request.user:
        # redirect them to the /course directory with message
        messages.info(request, 'Only Professor can post and update')
        return HttpResponseRedirect('/course')

    if request.method == 'POST':
        form = CourseUpdateForm(request.user.id, request.POST)
        if form.is_valid():
            new_update = CourseUpdate(course=course)
            new_update.course = course;
            new_update.title = form.cleaned_data.get('title')
            new_update.content = form.cleaned_data.get('content')
            new_update.creator = request.user
            new_update.save()

            # Next 4 lines handle sending an email to class roster
            # grab list of students in the course
            students_in_course = course.students.all().filter()
            # TODO: course variables contains (slug: blah blah)
            subject = "{0} has posted an update to {1}".format(request.user, course)
            content = "{0}\n\n www.grepthink.com".format(new_update.content)
            send_email(students_in_course, "noreply@grepthink.com", subject, content)
            messages.add_message(request, messages.SUCCESS, "Email Sent!")

            return redirect(view_one_course, course.slug)
    else:
        form = CourseUpdateForm(request.user.id)

    return render(
        request, 'courses/update_course.html',
        {'form': form, 'course': course, 'page_name': page_name, 'page_description': page_description, 'title': title}
    )


@login_required
def update_course_update(request, slug, id):
    """
    Edit an update for a given course
    """
    course = get_object_or_404(Course, slug=slug)
    update = get_object_or_404(CourseUpdate, id=id)

    if request.user.profile.isGT:
        pass
    elif update.creator != request.user:
        return redirect(view_one_course, course.slug)

    if request.method == 'POST':
        form = CourseUpdateForm(request.user.id, request.POST)
        if form.is_valid():
            update.course = course;
            update.title = form.cleaned_data.get('title')
            update.content = form.cleaned_data.get('content')
            if not request.user.profile.isGT:
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

    if update.creator == request.user or request.user.prfile.isGT:
        update.delete()

    return redirect(view_one_course, course.slug)


def lock_interest(request, slug):
    """
    Lock the interest for a course
    """
    course = get_object_or_404(Course, slug=slug)
    if course.limit_interest:
        course.limit_interest = False
    else:
        course.limit_interest = True

    course.save()
    return redirect(view_one_course, course.slug)


@login_required
def email_roster(request, slug):
    cur_course = get_object_or_404(Course, slug=slug)
    page_name = "Email Roster"
    page_description = "Emailing members of Course: %s" % (cur_course.name)
    title = "Email Student Roster"

    students_in_course = cur_course.get_students()

    count = len(students_in_course) or 0
    addcode = cur_course.addCode

    form = EmailRosterForm()
    if request.method == 'POST':
        # send the current user.id to filter out
        form = EmailRosterForm(request.POST, request.FILES)
        # if form is accepted
        if form.is_valid():
            # the courseID will be gotten from the form
            data = form.cleaned_data
            subject = data.get('subject')
            content = data.get('content')

            # attachment = request.FILES['attachment']
            # if attachment:
            #     handle_file(attachment)

            send_email(students_in_course, request.user.email, subject, content)
            messages.add_message(request, messages.SUCCESS, "Email Sent!")

            return redirect('view_one_course', slug)
        else:
            # redirect to error
            print("EmailRosterForm not valid")

    return render(request, 'courses/email_roster.html', {
        'slug': slug, 'form': form, 'count': count, 'students': students_in_course,
        'addcode': addcode, 'cur_course': cur_course,
        'page_name': page_name, 'page_description': page_description,
        'title': title
    })


@login_required
def email_csv(request, slug):
    cur_course = get_object_or_404(Course, slug=slug)
    page_name = "Invite Students"
    page_description = "Invite Students via CSV Upload"
    title = "Invite Students"

    addcode = cur_course.addCode
    recipients = []
    if 'recipients' in request.session:
        recipients = request.session['recipients']

    print("in email_csv: ", recipients, "request.method:", request.method)

    form = EmailRosterForm()
    if request.method == 'POST':
        form = EmailRosterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            subject = data.get('subject')
            content = data.get('content')

            print("recipients in email_csv", recipients)
            send_email(recipients, request.user.email, subject, content)
            messages.add_message(request, messages.SUCCESS, "Email Sent!")

            return redirect('view_one_course', slug)

        else:
            print("Form not valid!")

    return render(request, 'courses/email_roster_with_csv.html', {'count': len(recipients),
                                                                  'slug': slug, 'form': form, 'addcode': addcode,
                                                                  'students': recipients,
                                                                  'page_name': page_name,
                                                                  'page_description': page_description, 'title': title
                                                                  })


@login_required
def upload_csv(request, slug):
    page_name = "Upload CSV File"
    page_description = "CSV Upload"
    title = "Upload CSV"
    course = get_object_or_404(Course, slug=slug)

    recipients = []

    form = UploadCSVForm()
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data

            csv_file = data.get('csv_file')

            csv_dict = parse_csv(csv_file)

            for student in csv_dict:
                recipients.append(csv_dict[student])

            request.session['recipients'] = recipients

            return redirect(email_csv, slug)
        else:
            print("form is invalid")

    return render(request, 'core/upload_csv.html', {
        'slug': slug, 'form': form, 'course': course,
        'page_name': page_name, 'page_description': page_description, 'title': title
    })


import xlwt


@login_required
def export_xls(request, slug):
    page_name = "Export Course"
    page_description = "Save the current course's projects and associated members in an excel spreadsheet"
    title = "Export Course"
    course = get_object_or_404(Course, slug=slug)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="course_overview.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(course.name)

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    # header row
    ws.write(row_num, 0, course.name, font_style)
    ws.write(row_num, 1, course.term, font_style)
    ws.write(row_num, 2, course.year, font_style)

    projects = Project.objects.filter(course=course)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    # PROJECT SECTION OF SPREADSHEET
    for proj in projects:
        row_num += 2
        members = proj.get_members()
        ws.write(row_num, 0, proj.title, font_style)
        row_num += 1
        ws.write(row_num, 1, "TA:", font_style)
        ws.write(row_num, 2, proj.ta.email, font_style)
        row_num += 1
        ws.write(row_num, 1, "TA Meeting:", font_style)
        ws.write(row_num, 2, proj.ta_time, font_style)
        row_num += 1
        ws.write(row_num, 1, "Location:", font_style)
        ws.write(row_num, 2, proj.ta_location, font_style)
        row_num += 2
        ws.write(row_num, 1, "Members:", font_style)
        for mem in members:
            row_num += 1
            ws.write(row_num, 2, mem.email, font_style)

    students_num = Enrollment.objects.filter(course=course, role="student")
    projects_num = projects_in_course(course.slug)
    students_projects = []
    students_projects_not = []

    # DISPLAY PROJECTLESS SECTION OF SPREADSHEET
    for i in projects_num:
        for j in i.members.all():
            if not j in students_projects:
                students_projects.append(j)

    for i in students_num:
        if not i.user in students_projects:
            students_projects_not.append(i.user)

    row_num += 3
    ws.write(row_num, 0, "Students without a Project", font_style)
    for stud in students_projects_not:
        row_num += 1
        ws.write(row_num, 1, stud.email, font_style)

    wb.save(response)
    return response


@login_required
def export_interest(request, slug):
    """
    Exports the interest for each project to a csv
    """
    page_name = "Export Course Interest"
    page_description = "Save the current course's projects and associated Interests in an excel spreadsheet"
    title = "Export Course"
    course = get_object_or_404(Course, slug=slug)
    students = course.students.all()

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="project_preference.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(course.name)

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    # header row
    ws.write(row_num, 0, "USER", font_style)
    ws.write(row_num, 1, "PROJECT", font_style)
    ws.write(row_num, 2, "INTEREST", font_style)
    ws.write(row_num, 3, "REASON", font_style)

    projects = Project.objects.filter(course=course)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    no_interest_students = []

    # PROJECT SECTION OF SPREADSHEET
    for stud in students:
        # interest for current student\
        interest = Interest.objects.filter(user=stud)
        # if the student has interests
        if interest:
            # for each interest
            for i in interest:
                # if the interest is a project in the current course
                if i.project_interest.first() not in projects:
                    continue

                row_num += 1
                ws.write(row_num, 0, stud.username, font_style)
                ws.write(row_num, 1, i.project_interest.first().title)
                ws.write(row_num, 2, i.interest)
                ws.write(row_num, 3, i.interest_reason)

        else:
            no_interest_students.append(stud.username)

    row_num += 3
    ws.write(row_num, 0, "NO INTEREST", font_style)
    for stud in no_interest_students:
        row_num += 1
        ws.write(row_num, 0, stud)

    wb.save(response)
    return response


@login_required
def claim_projects(request, slug):
    page_name = "Claim Projects"
    page_description = "Select the projects that you are assigned to"
    title = "Claim Projects"
    course = get_object_or_404(Course, slug=slug)
    user = request.user
    profile = Profile.objects.get(user=user)
    projects = course.projects.all()
    claimed_projects = profile.claimed_projects.all()
    filtered = profile.claimed_projects.filter(course=course)

    available = []
    for proj in projects:
        found = False
        for p in filtered:
            if (proj == p):
                found = True
        if not found:
            available.append(proj)

    if request.method == 'POST':

        if request.POST.get('remove_claim'):
            proj_name = request.POST.get('remove_claim')
            to_delete = get_object_or_404(Project, title=proj_name)
            to_delete.ta = course.creator
            to_delete.save()
            profile.claimed_projects.remove(to_delete)
            profile.save()
            messages.add_message(request, messages.SUCCESS, "Project's TA Fields updated.")

            return redirect(view_one_course, course.slug)

        if request.POST.get('select_projects'):
            to_claim = request.POST.getlist('select_projects')

            # manally search for project object with the same title
            to_claim_projects = []
            for proj in projects:
                for title in to_claim:
                    if proj.title == title:
                        to_add = get_object_or_404(Project, title=title)
                        to_claim_projects.append(to_add)

            for p in to_claim_projects:
                p.ta = request.user
                p.save()
                profile.claimed_projects.add(p)
                profile.save()
            messages.add_message(request, messages.SUCCESS, "Project's TA Fields updated.")
            return redirect(view_one_course, course.slug)

    return render(request, 'courses/claim_projects.html',
                  {'course': course, 'available': available, 'claimed_projects': claimed_projects,
                   'page_name': page_name, 'page_description': page_description, 'title': title
                   })
