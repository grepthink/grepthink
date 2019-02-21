from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from teamwork.apps.courses.models import get_user_active_courses, get_user_disabled_courses
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.core.urlresolvers import reverse
from django.contrib import messages

from teamwork.apps.courses.forms import JoinCourseForm
from teamwork.apps.courses.models import Course, Enrollment
from teamwork.apps.profiles.models import Alert
from teamwork.apps.projects.models import Project

from teamwork.apps.courses.views.CourseView import view_one_course
from teamwork.apps.courses.forms import CreateCourseForm, JoinCourseForm
from teamwork.apps.core.forms import UploadCSVForm
from teamwork.apps.core.helpers import *
from teamwork.apps.courses.views.EmailCourseView import email_csv

import csv
import xlwt

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
            {'courses': courses,'page_name' : page_name, 'page_description': page_description, 'title': title}
            )

@login_required
def view_courses(request):
    """
    Public method that takes a request, retrieves all course objects associated with request.user    
    """

    return _courses(request, get_user_active_courses(request.user))

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
        #redirect them to the /course directory
        messages.info(request,'Only Professor can create course!')
        return HttpResponseRedirect('/course')

    #If request is POST
    if request.method == 'POST':
        # send the current user.id to filter out
        form = CreateCourseForm(request.user.id,request.POST, request.FILES)
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
    return render(request, 'courses/create_course.html', {'form': form, 'page_name' : page_name, 'page_description': page_description, 'title': title})

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
                    if not Enrollment.objects.filter(user=request.user, course=i, role=role).exists():
                        #creates an enrollment relation with the current user and the selected course
                        Enrollment.objects.create(user=request.user, course=i, role=role)
                        Alert.objects.create(
                                sender=request.user,
                                to=i.creator,
                                msg=request.user.username + " used the addcode to enroll in " + i.name,
                                url=reverse('profile',args=[request.user.username]),
                                )
                    return redirect(view_one_course, i.slug)

            #returns to view courses
            return redirect(view_courses)
    else:
        form = JoinCourseForm(request.user.id)
    return render(request, 'courses/join_course.html', {'form': form, 'page_name' : page_name, 'page_description': page_description, 'title': title})

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
        'slug':slug, 'form':form, 'course':course,
        'page_name':page_name, 'page_description':page_description,'title':title
    })

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

    students_num = Enrollment.objects.filter(course = course, role="student")
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

def projects_in_course(slug):
    """
    Public method that takes a coursename, retreives the course object, returns
    a list of project objects
    """
    # Gets current course
    cur_course = Course.objects.get(slug=slug)

    # Gets projects in cur_course ordered by title
    projects = Project.objects.filter(course=cur_course).extra(\
    select={'lower_title':'lower(title)'}).order_by('lower_title')
    return projects
