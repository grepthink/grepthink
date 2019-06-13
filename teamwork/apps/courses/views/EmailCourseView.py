from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.views.decorators.csrf import csrf_exempt
from teamwork.apps.courses.models import Course
from teamwork.apps.courses.forms import EmailRosterForm
from teamwork.apps.courses.views.CourseView import view_one_course
from teamwork.apps.core.helpers import send_email
from teamwork.apps.projects.models import Project
import json
from django.contrib.auth.models import User

@csrf_exempt
def select_recipents(request, slug):
    if request.is_ajax():
        if request.method=='POST':
            data=request.POST.get('receivers')
            recipents=json.loads(data)
            cur_course = get_object_or_404(Course, slug=slug)
            cur_course.receivers=json.dumps(recipents)
            cur_course.save()
            return HttpResponse("Save recipents" + data)
        else:
            return HttpResponse("Not save")

@login_required
def email_roster(request, slug):

    cur_course = get_object_or_404(Course, slug=slug)
    page_name = "Email Roster"
    page_description = "Emailing members of Course: %s"%(cur_course.name)
    title = "Email Student Roster"
    staff = cur_course.get_staff()
    staff_ids=[o.id for o in staff]
    ta_list = cur_course.get_tas()
    
    all_projects=list(cur_course.projects.all())  
    complete_members_list=[]
    project_scrum_master=[]
    projects_list=[]
    

    for pro in all_projects:
        project_members=[]
        project_obj=get_object_or_404(Project,title=pro)
        pro = project_obj.get_members2()
        for i in pro:
            project_members.append(i.username)
        
        complete_members_list.append(project_members)
        project_scrum_master.append(project_obj.scrum_master.username)
        projects_list.append(project_obj.title)


    combined = zip(projects_list,project_scrum_master,complete_members_list)
    projects = [{"title": p[0], "members": p[2], "scrum_master": p[1]} for p in combined]
    

    students = cur_course.receivers
    students_in = json.loads(students)
    students_in_course= list(User.objects.filter(username__in=students_in))
   

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
        'slug':slug, 'form':form, 'students':complete_members_list,
        'scrum_master':project_scrum_master,'ta_list':ta_list,'addcode':addcode, 'cur_course':cur_course,
        'page_name':page_name, 'page_description':page_description,'projects_list':projects,
        'title':title, 'count':count
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
