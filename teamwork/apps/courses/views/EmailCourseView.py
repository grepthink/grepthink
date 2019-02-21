from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)

from teamwork.apps.courses.models import Course
from teamwork.apps.courses.forms import EmailRosterForm
from teamwork.apps.courses.views.CourseView import view_one_course
from teamwork.apps.core.helpers import send_email

@login_required
def email_roster(request, slug):
    cur_course = get_object_or_404(Course, slug=slug)
    page_name = "Email Roster"
    page_description = "Emailing members of Course: %s"%(cur_course.name)
    title = "Email Student Roster"

    staff = cur_course.get_staff()
    staff_ids=[o.id for o in staff]
    students_in_course = list(cur_course.students.exclude(id__in=staff_ids))

    count = len(students_in_course) or 0
    addcode = cur_course.addCode

    form = EmailRosterForm()
    if request.method == 'POST':
        # send the current user.id to filter out
        form = EmailRosterForm(request.POST, request.FILES)
        #if form is accepted
        if form.is_valid():
            #the courseID will be gotten from the form
            data = form.cleaned_data
            subject = data.get('subject')
            content = data.get('content')

            response = send_email(students_in_course, request.user.email, subject, content)

            if isinstance(response, HttpResponse):
                messages.add_message(request, messages.INFO, response.content)

            return redirect('view_one_course', slug)        

    return render(request, 'courses/email_roster.html', {
        'slug':slug, 'form':form, 'count':count, 'students':students_in_course,
        'addcode':addcode, 'cur_course':cur_course,
        'page_name':page_name, 'page_description':page_description,
        'title':title
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

    print("in email_csv: ",recipients, "request.method:", request.method)

    form = EmailRosterForm()
    if request.method == 'POST':
        form = EmailRosterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            subject = data.get('subject')
            content = data.get('content')

            print("recipients in email_csv",recipients)
            send_email(recipients, request.user.email, subject, content)
            messages.add_message(request, messages.SUCCESS, "Email Sent!")

            return redirect('view_one_course', slug)

        else:
            print("Form not valid!")

    return render(request, 'courses/email_roster_with_csv.html', { 'count':len(recipients),
        'slug':slug, 'form':form, 'addcode':addcode, 'students':recipients,
        'page_name':page_name, 'page_description':page_description,'title':title
        })
