from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)

from teamwork.apps.profiles.models import Profile
from teamwork.apps.courses.models import Course
from teamwork.apps.projects.models import Interest, Project

from teamwork.apps.courses.views.CourseView import view_one_course

from teamwork.apps.courses.forms import ShowInterestForm

import csv
import xlwt

@login_required
def show_interest(request, slug):
    """
    public method that takes in a slug and generates a form for the user
    to show interest in all projects in a given course
    """
    profile = Profile.objects.prefetch_related('user__enrollment').filter(user=request.user).first()
    # current course
    cur_course = get_object_or_404(Course.objects.prefetch_related('projects', 'creator'), slug=slug)
    # projects in current course
    projects = cur_course.projects.all().extra(\
    select={'lower_title':'lower(title)'}).order_by('lower_title')
    # enrollment objects containing current user
    user_courses = profile.user.enrollment.all()

    user = request.user

    page_name = "Show Interest"
    page_description = "Show Interest in Projects for %s"%(cur_course.name)
    title = "Show Interest"

    #if user is professor
    if profile.isProf:
        #redirect them with a message
        messages.info(request,'Professor cannot show interest')
        return HttpResponseRedirect('/course')

    #if not enough projects
    if not projects.count():
        #redirect them with a message
        messages.info(request,'No projects to show interest in!')
        return HttpResponseRedirect('/course')

    # if course has disabled setting interest
    if cur_course.limit_interest:
        #redirect them with a message
        messages.info(request,'Can no longer show interest!')
        return HttpResponseRedirect('/course')

    # if current course not in users enrolled courses
    if not cur_course in user_courses and cur_course.creator != profile.user:
        messages.info(request,'You are not enrolled in this course')
        return HttpResponseRedirect('/course')


    # TODO: SHOULD ALSO HAVE CHECK TO SEE IF USER ALREADY HAS SHOWN INTEREST

    if request.method == 'POST':
        form = ShowInterestForm(request.user.id, request.POST, slug = slug)
        if form.is_valid():
            data=form.cleaned_data
            #Gets first choice, creates interest object for it

            # Clear all interest objects where user is current user and for this course, avoid duplicates
            for project in cur_course.projects.all():
                user_interests = Interest.objects.filter(project_interest=project, user=request.user)
                if user_interests is not None: user_interests.delete()

            # all_interests = Interest.objects.filter(project_interest=projects)
            # interests = all_interests.filter(user=user)
            # interests = Interest.objects.filter(project_interest=projects, user=user)
            # if interests is not None: interests.delete()

            projectCount = len(projects)

            if projectCount >= 1:
                choice_1 = data.get('projects')
                r1 = data.get('p1r')
                choice_1.interest.add(Interest.objects.create(user=user, interest=5, interest_reason=r1))
                choice_1.save()

            #Gets second choice, creates interest object for it
            if projectCount >= 2:
                choice_2 = data.get('projects2')
                r2 = data.get('p2r')
                choice_2.interest.add(Interest.objects.create(user=user, interest=4, interest_reason=r2))
                choice_2.save()

            #Gets third choice, creates interest object for it
            if projectCount >= 3:
                choice_3 = data.get('projects3')
                r3 = data.get('p3r')
                choice_3.interest.add(Interest.objects.create(user=user, interest=3, interest_reason=r3))
                choice_3.save()

            #Gets fourth choice, creates interest object for it
            if projectCount >= 4:
                choice_4 = data.get('projects4')
                r4 = data.get('p4r')
                choice_4.interest.add(Interest.objects.create(user=user, interest=2, interest_reason=r4))
                choice_4.save()

            #Gets fifth choice, creates interest object for it
            if projectCount >= 5:
                choice_5 = data.get('projects5')
                r5 = data.get('p5r')
                choice_5.interest.add(Interest.objects.create(user=user, interest=1, interest_reason=r5))
                choice_5.save()

            messages.success(request, "You have succesfully submitted your interest")


            return redirect(view_one_course, slug)

    else:
        form = ShowInterestForm(request.user.id, slug = slug)

    return render(
            request, 'courses/show_interest.html',
            {'form': form,'cur_course': cur_course, 'page_name' : page_name, 'page_description': page_description, 'title': title}
            )

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
        #interest for current student\
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
