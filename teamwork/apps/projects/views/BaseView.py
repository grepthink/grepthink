# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect, JsonResponse)

from teamwork.apps.courses.models import *
from teamwork.apps.courses.forms import *
from teamwork.apps.projects.models import *
from teamwork.apps.projects.forms import *
from teamwork.apps.projects.views.MyProjectsView import *

from teamwork.apps.core.helpers import send_email

@login_required
def create_project(request):
    """
    Public method that creates a form and renders the request to create_project.html
    """
    # Populate page info with new project headers/title
    page_name = "Create Project"
    page_description = "Post a new project"
    title = "Create Project"

    # Get the current user, once and only once.
    user = request.user

    # profile = Profile.objects.get(user=user)
    profile = user.profile

    # current courses the user is in
    cur_courses = user.enrollment.all()

    no_postable_classes = False

    # my_created_courses = Course.objects.filter(creator=user)
    my_created_courses = user.course_creator.all()

    if user.profile.isGT:
        pass
    # If user is in 0 courses
    elif not cur_courses and not my_created_courses:
        # Redirect them to homepage and tell them to join a course
        messages.info(request,
                      'You need to join a course before creating projects!')
        return HttpResponseRedirect('/')

    if len(cur_courses) == len(cur_courses.filter(limit_creation=True)):
        no_postable_classes = True

    if user.profile.isGT:
        pass
    elif cur_courses and no_postable_classes and not profile.isProf:
        # Redirect them to homepage and tell them to join a course
        messages.info(request, 'Professor has disabled Project Creation!')
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = CreateProjectForm(user.id, request.POST)
        if form.is_valid():
            # Create an object for the input
            project = Project()

            # Fill all the simple fields and save project object.
            project.slug = form.cleaned_data.get('slug')
            project.title = form.cleaned_data.get('title')
            project.tagline = form.cleaned_data.get('tagline')
            project.creator = user
            project.avail_mem = form.cleaned_data.get('accepting')
            project.sponsor = form.cleaned_data.get('sponsor')
            project.teamSize = form.cleaned_data.get('teamSize') or 4
            project.no_request = form.cleaned_data.get('no_request')
            project.weigh_interest = form.cleaned_data.get('weigh_interest') or 0
            project.weigh_know = form.cleaned_data.get('weigh_know') or 0
            project.weigh_learn = form.cleaned_data.get('weigh_learn') or 0
            project.content = form.cleaned_data.get('content')



            # Course the project is in
            in_course = form.cleaned_data.get('course')

            # Init TA of Project ot be the Professor
            # project.ta = in_course.creator
            project.save()

            # Add project to course
            in_course.projects.add(project)

            if not user.profile.isGT:
                if user not in in_course.get_staff():
                    project.scrum_master = request.user
                project.save()

            # Local list of memebers, used to create Membership objects
            # Now not getting this list through the form, because this list is created
            # using select2 javascript.
            members = request.POST.getlist('members')

            # Add skills to the project
            if request.POST.get('desired_skills'):
                skills = request.POST.getlist('desired_skills')
                for s in skills:
                    s_lower = s.lower()
                    # Check if lowercase version of skill is in db
                    if Skills.objects.filter(skill=s_lower):
                        # Skill already exists, then pull it up
                        desired_skill = Skills.objects.get(skill=s_lower)
                    else:
                        # Add the new skill to the Skills table
                        desired_skill = Skills.objects.create(skill=s_lower)
                        # Save the new object
                        desired_skill.save()
                    # Add the skill to the project (as a desired_skill)
                    project.desired_skills.add(desired_skill)
                    project.save()
#------------------------------------------------------------------------
            if request.POST.get('desired_techs'):
                techs = request.POST.getlist('desired_techs')
                for s in techs:
                    s_lower = s.lower()
                    # Check if lowercase version of tech is in db
                    if Techs.objects.filter(tech=s_lower):
                        # Skill already exists, then pull it up
                        desired_tech = Techs.objects.get(tech=s_lower)
                    else:
                        # Add the new skill to the Skills table
                        desired_tech = Techs.objects.create(tech=s_lower)
                        # Save the new object
                        desired_tech.save()
                    # Add the skill to the project (as a desired_skill)
                    project.desired_techs.add(desired_tech)
                    project.save()
#-----------------------------------------------------------------------------


            # Loop through the members in the object and make m2m rows for them
            for i in members:
                i_user = User.objects.get(username=i)
                mem_courses = Course.get_my_courses(i_user)
                if in_course in mem_courses:
                    Membership.objects.create(
                        user=i_user, project=project, invite_reason='')

            # Don't add the professor to the project (will still be owner)
            if profile.isGT:
                pass
            elif user not in in_course.get_staff():
                Membership.objects.create(
                    user=user, project=project, invite_reason='')

            # we dont have to save again because we do not touch the project object
            # we are doing behind the scenes stuff (waves hand)
            return redirect(view_projects)
        else:
            return redirect(view_projects)
    else:
        # Send form for initial project creation
        form = CreateProjectForm(request.user.id)
    return render(request, 'projects/create_project.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title, 'form': form})

@login_required
def email_project(request, slug):
    project = get_object_or_404(Project, slug=slug)
    page_name = "Email Project"
    page_description = "Emailing members of Project: %s"%(project.title)
    title = "Email Project"

    students_in_project = project.get_members()

    count = len(students_in_project) or 0

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

            send_email(students_in_project, request.user.email, subject, content)
            messages.add_message(request, messages.SUCCESS, "Email Sent!")

            return redirect('view_one_project', slug)
        else:
            # redirect to error
            print("EmailRosterForm not valid")

    return render(request, 'projects/email_project.html', {
        'slug':slug, 'form':form, 'count':count, 'students':students_in_project,
        'project':project,
        'page_name':page_name, 'page_description':page_description,
        'title':title
    })

def get_user_role(user, course):
    """
    returns the role of the user in the course
    """
    if not user.profile.isGT:
        userEnrollment = Enrollment.objects.filter(user=user, course=course).first()
        if userEnrollment is None:
            # then the current user is not enrolled in the course this project belongs to
            user_role = 'not enrolled'
        else:
            user_role = userEnrollment.role
    else: #maybe don't need a GT user_role. profile.isGT is probably better -kp
        user_role = 'GT'

    return user_role
