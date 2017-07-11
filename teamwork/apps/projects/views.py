from django.contrib import messages
from django.contrib.auth.decorators import login_required
from teamwork.apps.courses.models import *
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User

from teamwork.apps.core.models import *
from teamwork.apps.courses.models import *

from .forms import *
from .models import *

import json


def _projects(request, projects):
    """
    Private method that will be used for paginator once I figure out how to get it working.
    """
    page = request.GET.get('page')


    # Populate with page name and title
    page_name = "My Projects"
    page_description = "Projects created by " + request.user.username
    title = "My Projects"


    return render(request, 'projects/view_projects.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title,
        'projects': projects})


@login_required
def view_projects(request):
    """
    Public method that takes a request, retrieves all Project objects from the model,
    then calls _projects to render the request to template view_projects.html
    """
    my_projects = Project.get_my_projects(request.user)
    my_created = Project.get_created_projects(request.user)
    projects = my_projects | my_created
    projects = list(set(projects))

    return _projects(request, projects)


def view_meetings(request, slug):
    """
    Public method that takes a request and a slug, retrieves the Project object
    from the model with given project slug.  Renders projects/view_project.html

    Passing status check unit test in test_views.py.
    """
    from django.utils.safestring import mark_safe
    project = get_object_or_404(Project, slug=slug)

    find_meeting(slug)

    readable = ""
    if project.readable_meetings:
        jsonDec = json.decoder.JSONDecoder()
        readable = jsonDec.decode(project.readable_meetings)

    # Get the course given a project wow ethan great job keep it up.
    course = Course.objects.get(projects=project)

    print(project.meetings)

    #meetings = mark_safe([{'start': '2017-04-09T08:00:00', 'end': '2017-04-09T20:30:00', 'title': 'Meeting'}])

    meetings = mark_safe(project.meetings)


    # Populate with project name and tagline
    page_name = project.title or "Project"
    page_description = project.tagline or "Meeting Times"
    title = project.title or "Meetings"

    return render(request, 'projects/meeting_times.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title,
        'project': project, 'course' : course, 'json_events': meetings})



def view_one_project(request, slug):
    """
    Public method that takes a request and a slug, retrieves the Project object
    from the model with given project slug.  Renders projects/view_project.html

    Passing status check unit test in test_views.py.
    """

    project = get_object_or_404(Project, slug=slug)
    updates = project.get_updates()
    resources = project.get_resources()

    find_meeting(slug)

    readable = ""
    if project.readable_meetings:
        jsonDec = json.decoder.JSONDecoder()
        readable = jsonDec.decode(project.readable_meetings)

    # Get the course given a project wow ethan great job keep it up.
    course = Course.objects.get(projects=project)


    # Populate with project name and tagline
    page_name = project.title or "Project"
    page_description = project.tagline or "Tagline"
    title = project.title or "Project"


    print(updates)

    return render(request, 'projects/view_project.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title,
        'project': project, 'updates': updates, 'course' : course,
        'meetings': readable, 'resources': resources, 'json_events': project.meetings})


def select_members(request):
    if request.method == 'POST' and request.is_ajax():
        return HttpResponse("Form Submitted")

    elif request.method == 'GET' and request.is_ajax():
        # JSON prefers dictionaries over lists.
        data = dict()
        # A list in a dictionary, accessed in select2 ajax
        data['items'] = []
        q = request.GET.get('q')
        if q is not None:
            results = User.objects.filter(
                Q( first_name__contains = q ) |
                Q( last_name__contains = q ) |
                Q( username__contains = q ) ).order_by( 'username' )
        for u in results:
            data['items'].append({'id': u.username, 'text': u.username})
        return JsonResponse(data)


    return HttpResponse("Failure")

def edit_select_members(request, slug):
    if request.method == 'POST' and request.is_ajax():
        return HttpResponse("Form Submitted")

    elif request.method == 'GET' and request.is_ajax():
        # JSON prefers dictionaries over lists.
        data = dict()
        # A list in a dictionary, accessed in select2 ajax
        data['items'] = []
        q = request.GET.get('q')
        if q is not None:
            results = User.objects.filter(
                Q( first_name__contains = q ) |
                Q( last_name__contains = q ) |
                Q( username__contains = q ) ).order_by( 'username' )
        for u in results:
            data['items'].append({'id': u.username, 'text': u.username})
        return JsonResponse(data)


    return HttpResponse("Failure")

def add_desired_skills(request, slug):
    if request.method == 'GET' and request.is_ajax():
        # JSON prefers dictionaries over lists.
        data = dict()
        # A list in a dictionary, accessed in select2 ajax
        data['items'] = []
        q = request.GET.get('q')
        if q is not None:
            results = Skills.objects.filter(
                Q( skill__contains = q ) ).order_by( 'skill' )
        for s in results:
            data['items'].append({'id': s.skill, 'text': s.skill})
        return JsonResponse(data)


    return HttpResponse("Failure")

def create_desired_skills(request):
    if request.method == 'GET' and request.is_ajax():
        # JSON prefers dictionaries over lists.
        data = dict()
        # A list in a dictionary, accessed in select2 ajax
        data['items'] = []
        q = request.GET.get('q')
        if q is not None:
            results = Skills.objects.filter(
                Q( skill__contains = q ) ).order_by( 'skill' )
        for s in results:
            data['items'].append({'id': s.skill, 'text': s.skill})
        return JsonResponse(data)


    return HttpResponse("Failure")

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

    profile = Profile.objects.get(user=user)

    # Enrollment objects containing current user
    enroll = Enrollment.objects.filter(user=user)
    # Current courses user is in
    cur_courses = Course.objects.filter(enrollment__in=enroll)
    no_postable_classes = False

    my_created_courses = Course.objects.filter(creator=user.username)

    # If user is in 0 courses
    if len(enroll) == 0 and len(my_created_courses) == 0:
        # Redirect them to homepage and tell them to join a course
        messages.info(request,
                      'You need to join a course before creating projects!')
        return HttpResponseRedirect('/')

    if len(cur_courses) == len(cur_courses.filter(limit_creation=True)):
        no_postable_classes = True

    if len(enroll) >= 1 and no_postable_classes and not profile.isProf:
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
            project.creator = request.user.username
            project.avail_mem = form.cleaned_data.get('accepting')
            project.sponsor = form.cleaned_data.get('sponsor')
            project.teamSize = form.cleaned_data.get('teamSize') or 4
            project.weigh_interest = form.cleaned_data.get('weigh_interest') or 0
            project.weigh_know = form.cleaned_data.get('weigh_know') or 0
            project.weigh_learn = form.cleaned_data.get('weigh_learn') or 0
            project.content = form.cleaned_data.get('content')

            project.save()

            in_course = form.cleaned_data.get('course')
            in_course.projects.add(project)

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

            # Loop through the members in the object and make m2m rows for them
            for i in members:
                i_user = User.objects.get(username=i)
                mem_courses = Course.get_my_courses(i_user)
                if in_course in mem_courses:
                    Membership.objects.create(
                        user=i_user, project=project, invite_reason='')

            # Don't add the professor to the project (will still be owner)
            if not profile.isProf:
                Membership.objects.create(
                    user=user, project=project, invite_reason='')

            # we dont have to save again because we do not touch the project object
            # we are doing behind the scenes stuff (waves hand)
            return redirect(view_projects)
        else:
            messages.info(request,'Errors in form')
    else:
        # Send form for initial project creation
        form = CreateProjectForm(request.user.id)
    return render(request, 'projects/create_project.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title, 'form': form})


@login_required
def edit_project(request, slug):
    """
    Public method that serves the form allowing a user to edit a project
    Based off courses/views.py/edit_course
    """
    project = get_object_or_404(Project, slug=slug)

    # Populate page info with edit project title/name
    page_name = "Edit Project"
    page_description = "Make changes to " + project.title
    title = "Edit Project"

    # if user is not project owner or they arent in the member list
    if not request.user.username == project.creator and request.user not in project.members.all():
        #redirect them with a message
        messages.info(request, 'Only Project Owner can edit project!')
        return HttpResponseRedirect('/project/all')

    if request.POST.get('delete_project'):
        # ## Check that the current user is the project owner
        # if not request.user.username == project.creator:
        #     messages.info(request,'Only project owner can delete project.')
        # else:
        project.delete()
        return HttpResponseRedirect('/project/all')

    # Add a member to the project
    if request.POST.get('members'):
        # Get the course that this project is in
        this_course = Course.objects.get(projects=project)
        # Get the members to add, as a list
        members = request.POST.getlist('members')

        curr_members = Membership.objects.filter(project=project)

        # Create membership objects for the newly added members
        for uname in members:
            mem_to_add = User.objects.get(username=uname)
            mem_courses = Course.get_my_courses(mem_to_add)
            # Don't add a member if they already have membership in project
            # Confirm that the member is a part of the course
            # List comprehenshion: loops through this projects memberships in order
            #   to check if mem_to_add is in the user field of a current membership.
            if this_course in mem_courses and mem_to_add not in [mem.user for mem in curr_members]:
                Membership.objects.create(
                    user=mem_to_add, project=project, invite_reason='')
        return redirect(edit_project, slug)

    # Remove a user from the project
    if request.POST.get('remove_user'):
        f_username = request.POST.get('remove_user')
        f_user = User.objects.get(username=f_username)
        to_delete = Membership.objects.filter(user=f_user, project=project)
        for mem_obj in to_delete:
            mem_obj.delete()
        return redirect(edit_project, slug)

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
        return redirect(edit_project, slug)

    # Remove a desired skill from the project
    if request.POST.get('remove_desired_skill'):
        skillname = request.POST.get('remove_desired_skill')
        to_delete = Skills.objects.get(skill=skillname)
        project.desired_skills.remove(to_delete)
        return redirect(edit_project, slug)

    if request.method == 'POST':
        form = EditProjectForm(request.user.id, request.POST)

        if form.is_valid():
            # edit the project object, omitting slug
            project.title = form.cleaned_data.get('title')
            project.tagline = form.cleaned_data.get('tagline')
            project.avail_mem = form.cleaned_data.get('accepting')
            project.sponsor = form.cleaned_data.get('sponsor')
            project.teamSize = form.cleaned_data.get('teamSize')
            project.weigh_interest = form.cleaned_data.get('weigh_interest') or 0
            project.weigh_know = form.cleaned_data.get('weigh_know') or 0
            project.weigh_learn = form.cleaned_data.get('weigh_learn') or 0
            # Project content
            project.content = form.cleaned_data.get('content')
            project.lower_time_bound = form.cleaned_data.get('lower_time_bound')
            project.upper_time_bound = form.cleaned_data.get('upper_time_bound')

            project.save()

            # Not sure if view_one_project redirect will work...
            return redirect(view_one_project, project.slug)
    else:
        form = EditProjectForm(request.user.id, instance=project)
    return render(request, 'projects/edit_project.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title,
        'form': form, 'project': project})


@login_required
def post_update(request, slug):
    """
    Post an update for a given project
    """
    project = get_object_or_404(Project, slug=slug)

    if not request.user.username == project.creator and request.user not in project.members.all(
    ):
        #redirect them with a message
        messages.info(request, 'Only current members can post an update for a project!')
        return HttpResponseRedirect('/project/all')

    if request.method == 'POST':
        form = UpdateForm(request.user.id, request.POST)
        if form.is_valid():
            new_update = ProjectUpdate(project=project)
            new_update.update = form.cleaned_data.get('update')
            new_update.update_title = form.cleaned_data.get('update_title')
            new_update.user = request.user
            new_update.save()
            return redirect(view_one_project, project.slug)
    else:
        form = UpdateForm(request.user.id)
    return render(request, 'projects/post_update.html',
                  {'form': form,
                   'project': project})

@login_required
def resource_update(request, slug):

    project = get_object_or_404(Project, slug=slug)

    if not request.user.username == project.creator and request.user not in project.members.all(
    ):
        #redirect them with a message
        messages.info(request, 'Only current members can post an update for a project!')
        return HttpResponseRedirect('/project/all')

    if request.method == 'POST':
        form = ResourceForm(request.user.id, request.POST)
        if form.is_valid():
            new_update = ResourceUpdate(project=project)
            new_update.src_link = form.cleaned_data.get('src_link')
            new_update.src_title = form.cleaned_data.get('src_title')
            new_update.user = request.user
            new_update.save()
            return redirect(view_one_project, project.slug)
    else:
        form = ResourceForm(request.user.id)

    return render(request, 'projects/add_resource.html',{'form': form, 'project': project})

@login_required
def tsr_update(request, slug):
    """
    public method that takes in a slug and generates a form for the user
    to show interest in all projects in a given course
    """
    user = request.user
    # current course
    cur_course = get_object_or_404(Project, slug=slug)
    # projects in current course
    member_num=len(cur_course.members.all())
    members=list()
    emails=list()
    for i in range(member_num):
        members.append(cur_course.members.all()[i])
        emails.append(cur_course.members.all()[i].email)
    print(members)
    print(emails)


    # enrollment objects containing current user
    #enroll = Enrollment.objects.filter(user=request.user)
    # current courses user is in
    #user_courses = Course.objects.filter(enrollment__in=enroll)

    page_name = "TSR Update"
    page_description = "Update TSR form"
    title = "TSR Update"

    if request.method == 'POST':
        form = TSRUpdateForm(request.user.id, request.POST)
        if form.is_valid():
            data=form.cleaned_data

            return redirect(view_projects)

    else:
        form = TSRUpdateForm(request.user.id, request.POST)


    return render(request, 'projects/tsr_update.html', {'form': form,'cur_course': cur_course, 'page_name' : page_name, 'page_description': page_description, 'title': title})

def find_meeting(slug):
    """
    Find and store possible meeting time for a given project
    """
    # Gets current project
    project = get_object_or_404(Project, slug=slug)
    course = Course.objects.get(projects=project)
    # low = project.lower_time_bound
    # high = project.upper_time_bound

    # If project already has a list of meeting times, delete it
    if project.meetings is not None:
        project.meetings = ''
    if project.readable_meetings is not None:
         project.readable_meetings = ''

    # Stores avaliablity in list
    # event_list = project.generate_avail(low, high)
    event_list = project.generate_avail()
    readable_list = []

    for event in event_list:

        day = event['start'][8] + event['start'][9]
        day = int(day)
        day = dayofweek(day)
        s_hour = event['start'][11] + event['start'][12]
        s_minute = event['start'][14] + event['start'][15]

        s_hour = int(s_hour)
        s_minute = int(s_minute)

        e_hour = event['end'][11] + event['end'][12]
        e_minute = event['end'][14] + event['end'][15]
        e_hour = int(e_hour)
        e_minute = int(e_minute)

        event_string = "%s -> %02d:%02d - %02d:%02d"%(day, s_hour, s_minute, e_hour, e_minute)
        readable_list.append(event_string)

    # Adds meeting to model
    project.meetings = event_list
    project.save()

    project.readable_meetings = json.dumps(readable_list)
    project.save()

    return "Something"
    #return render(request, 'projects/view_projects.html',
    #              {'projects': projects})
