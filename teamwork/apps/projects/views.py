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
from django.urls import reverse

from teamwork.apps.core.models import *
from teamwork.apps.courses.models import *
from teamwork.apps.profiles.models import Alert
from teamwork.apps.core.helpers import *
from teamwork.apps.courses.views import view_one_course
from teamwork.apps.profiles.views import view_alerts

from teamwork.apps.courses.forms import EmailRosterForm
from .forms import *
from .models import *

from itertools import chain
import json
import math
import decimal

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

    return _projects(request, my_projects)

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
    
    scrum_master = project.scrum_master
    updates = project.get_updates()
    resources = project.get_resources()
    # Get the project owner for color coding stuff
    project_owner = project.creator.profile
    members = project.members.all()

    # Populate with project name and tagline
    page_name = project.title or "Project"
    page_description = project.tagline or "Tagline"
    title = project.title or "Project"

    # Get the course given a project wow ethan great job keep it up.
    course = project.course.first()
    staff = course.get_staff()

    asgs = list(course.assignments.all())
    asg_completed = []

    for i in asgs:
        for j in i.subs.all():
            if j.evaluator == request.user:
                asg_completed.append(i)
                break



    user = request.user
    profile = Profile.objects.get(user=user)

    # to reduce querys in templates -kp
    pending_members = project.pending_members.all()
    pending_count = len(pending_members)
    project_members = project.members.all()

    isProf = 0
    if request.user.profile.isProf:
        isProf = 1

    requestButton = 1
    if request.user in pending_members:
        requestButton = 0

    project_chat = reversed(project.get_chat())
    if request.method == 'POST':
        form = ChatForm(request.user.id, slug, request.POST)
        if form.is_valid():
            # Create a chat object
            chat = ProjectChat(author=request.user, project=project)
            chat.content = form.cleaned_data.get('content')
            chat.save()
            return redirect(view_one_project, project.slug)
        else:
            messages.info(request,'Errors in form')
    else:
        # Send form for initial project creation
        form = ChatForm(request.user.id, slug)

    find_meeting(slug)

    readable = ""
    if project.readable_meetings:
        jsonDec = json.decoder.JSONDecoder()
        readable = jsonDec.decode(project.readable_meetings)

    completed_tsrs = project.tsr.all()
    avg_dict = {}
    for i in completed_tsrs.all():
        if i.evaluatee in avg_dict.keys():
            avg_dict[i.evaluatee] = int(avg_dict[i.evaluatee]) + int(i.percent_contribution)
        else:
            avg_dict[i.evaluatee] = int(i.percent_contribution)

    avgs = []
    for key, item in avg_dict.items():
        con_avg = item / (len(completed_tsrs) / len(members))
        avgs.append((key, int(con_avg)))
    assigned_tsrs = course.assignments.filter(ass_type="tsr", closed=False)

    tsr_tuple={}

    if not request.user.profile.isGT:
        user_role = Enrollment.objects.filter(user=request.user, course=course).first().role
    else:
        user_role = 'GT'

    if request.user.profile.isGT or request.user.profile.isProf or user_role=="ta":
        for i in assigned_tsrs:
            for j in project.tsr.all():
                if j in i.subs.all():
                    tsr_tuple.setdefault(j.evaluatee, []).append([0, j, i])

        tsr_keys = tsr_tuple.keys()
        tsr_items = tsr_tuple.items()
        mem_count = len(members)
    else:
        tsr_keys = None
        tsr_items = None
        mem_count = None


    med = 100
    if len(members) > 0:
        med = int(100/len(members))
    mid = {'low' : int(med*0.7), 'high' : int(med*1.4)}
    today = datetime.now().date()
    

    #=======================
    #Analysis Tab Work 
    # Checks to see if analysis already exists for assignment specific TSRs, will generate analysis IF it does not already exist AND
    # TSR's completed. This means the correct amount of Tsr's for the assignment per project exist, with the correct matches to evaluator
    # and evaluatee
    
    #checks the course for each assignment of type tsr and goes through each to get the assignment number and associated analysis
    for each_assigned_tsr in assigned_tsrs: 
       
         assigned_tsr_number = each_assigned_tsr.ass_number
         existing_analysis = project.analysis.filter(tsr_number = assigned_tsr_number)

         #check to see if an instance of the analysis for a specific tsr assigned does not exist for the project
         #if it exists, skip over analysis generation completely, if not go through with next check
         if not existing_analysis.exists():
             completed_tsrs_per_ass_number = project.tsr.filter(ass_number = assigned_tsr_number)

             if mem_count == (len(completed_tsrs_per_ass_number)/mem_count):
                 tsr_exists = {}
                 
                 for each_member in members :
                     tsr_per_evaluator = completed_tsrs_per_ass_number.filter(evaluator = each_member)
                     
                     for each_evaluatee in members:
                         tsr_exists[str(each_member), str(each_evaluatee)] = tsr_per_evaluator.filter(evaluatee = each_evaluatee).exists()

                 num_distinct_tsrs = sum(tsr_exists.values())
                 if  len(completed_tsrs_per_ass_number) == num_distinct_tsrs :
                    #Put functions here
                    similarity_for_given_evals(project, assigned_tsr_number)
                    giving_outlier_scores(project, assigned_tsr_number)
                    tsr_word_count(project, assigned_tsr_number)
                    similarity_of_eval_history(project, assigned_tsr_number)
                    averages_for_all_evals(project, assigned_tsr_number)

                 else:
                     messages.warning(request, 'TSR' + str(assigned_tsr_number) + 'is not complete. All TSRs must be complete to generate analysis!')

#historical functions go here
    analysis_dicts={}

    for analysis_object in project.analysis.all():
            analysis_dicts.setdefault(analysis_object.analysis_type, []).append([analysis_object])            

    analysis_items = analysis_dicts.items()

    return render(request, 'projects/view_project.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title, 'members' : members, 'form' : form,
        'project': project, 'project_members':project_members, 'pending_members': pending_members, 'mem_count':mem_count,
        'requestButton':requestButton, 'avgs':avgs, 'assignments':asgs, 'asg_completed':asg_completed,'today':today,
        'pending_count':pending_count,'profile' : profile, 'scrum_master': scrum_master, 'staff':staff,
        'updates': updates, 'project_chat': project_chat, 'course' : course, 'project_owner' : project_owner,
        'meetings': readable, 'resources': resources, 'json_events': project.meetings, 'tsrs' : tsr_items, 'tsr_keys': tsr_keys, 
        'contribute_levels' : mid, 'assigned_tsrs': assigned_tsrs, 'all_analysis' : analysis_items})

def leave_project(request, slug):
    project = get_object_or_404(Project, slug=slug)
    members = project.members.all()
    pending_members = project.pending_members.all()
    f_user = request.user
    to_delete = Membership.objects.filter(user=f_user, project=project)

    remaining = Membership.objects.filter(project=project).exclude(user=f_user)


    if (f_user not in members):
        messages.warning(request, "You cannot leave a project you are not a member of!")
        HttpResponseRedirect('project/all')
    # check if they were the only member of the project
    elif len(members) == 1:
        messages.warning(request,
         "As the only member of the project, you must invite another to be the Project Owner, or delete the project via Edit Project!")
    else:
        # check if user that is being removed was Project Owner
        if f_user == project.creator:
            project.creator = remaining.first().user
        # check if user that is being removed was Scrum Master
        if f_user == project.scrum_master:
            project.scrum_master = remaining.first().user

        project.save()
        messages.info(request, "You have left {0}".format(project))

        # delete membership
        for mem_obj in to_delete:
            mem_obj.delete()

    return redirect(view_projects)

def request_join_project(request, slug):
    project = get_object_or_404(Project, slug=slug)
    project_members = project.members.all()
    pending_members = project.pending_members.all()

    if request.user in project_members:
        # TODO: send an error
        print("already in project, button shouldn't appear")
    elif request.user not in pending_members:
        # user wants to join project
        # add to pending members list of projects
        project.pending_members.add(request.user)
        project.save()

        # send email to project owner
        creator = project.creator
        subject = "{0} has requested to join {1}".format(request.user, project.title)
        # TODO: create link that goes directly to accept or deny
        content_text = "Please follow the link below to accept or deny {0}'s request.".format(request.user)
        content = "{0}\n\n www.grepthink.com".format(content_text)
        send_email(creator, "noreply@grepthink.com", subject, content)
        # notify user that their request has gone through successfully
        messages.add_message(request, messages.SUCCESS, "{0} has been notified of your request to join!".format(project.title))

        # TODO: send alert to project members and/or PO

        course = project.course.first()

        return redirect(view_one_course, course.slug)

    elif request.user in pending_members:
        # Cancel Request to join
        # remove member from pending list
        for mem in pending_members:
            if mem == request.user:
                project.pending_members.remove(mem)
                project.save()

        Alert.objects.create(
            sender=request.user,
            to=project.creator,
            msg=request.user.username + " has revoked there request to join " + project.title,
            url=reverse('view_one_project',args=[project.slug]),
            )

    return view_one_project(request, slug)

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

# used for querying members in EditProject, EditCourse
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

    # profile = Profile.objects.get(user=user)
    profile = user.profile

    # Enrollment objects containing current user
    # enroll = Enrollment.objects.filter(user=user)
    cur_courses = user.enrollment.all()
    # Current courses user is in
    # cur_courses = Course.objects.filter(enrollment__in=enroll)
    no_postable_classes = False

    # my_created_courses = Course.objects.filter(creator=user)
    my_created_courses = user.course_creator.all()

    if user.profile.isGT:
        pass
    # If user is in 0 courses
    elif len(cur_courses) == 0 and len(my_created_courses) == 0:
        # Redirect them to homepage and tell them to join a course
        messages.info(request,
                      'You need to join a course before creating projects!')
        return HttpResponseRedirect('/')

    if len(cur_courses) == len(cur_courses.filter(limit_creation=True)):
        no_postable_classes = True

    if user.profile.isGT:
        pass
    elif len(cur_courses) >= 1 and no_postable_classes and not profile.isProf:
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
            project.creator = request.user
            project.avail_mem = form.cleaned_data.get('accepting')
            project.sponsor = form.cleaned_data.get('sponsor')
            project.teamSize = form.cleaned_data.get('teamSize') or 4
            project.weigh_interest = form.cleaned_data.get('weigh_interest') or 0
            project.weigh_know = form.cleaned_data.get('weigh_know') or 0
            project.weigh_learn = form.cleaned_data.get('weigh_learn') or 0
            project.content = form.cleaned_data.get('content')
            project.scrum_master = request.user

            # Course the project is in
            in_course = form.cleaned_data.get('course')
            # Init TA of Project ot be the Professor
            project.ta = in_course.creator
            project.save()

            # Add project to course
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
            if profile.isGT:
                pass
            elif not profile.isProf:
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
def edit_project(request, slug):
    """
    Public method that serves the form allowing a user to edit a project
    Based off courses/views.py/edit_course
    """
    project = get_object_or_404(Project, slug=slug)
    course = project.course.first()
    project_owner = project.creator.profile
    members = project.members.all()

    # Populate page info with edit project title/name
    page_name = "Edit Project"
    page_description = "Make changes to " + project.title
    title = "Edit Project"

    # if user is not project owner or they arent in the member list
    if request.user.profile.isGT or request.user == course.creator:
        pass
    elif not request.user  in project.members.all():
        #redirect them with a message
        messages.warning(request, 'Only the Project Owner can make changes to this project!')
        return redirect(view_one_project, project.slug)

    if request.POST.get('delete_project'):
        # Check that the current user is the project owner
        if request.user == project.creator:
            project.delete()
        else:
            messages.warning(request,'Only project owner can delete project.')

        return HttpResponseRedirect('/project/all')

    # Add a member to the project
    if request.POST.get('members'):
        # Get the course that this project is in
        this_course = Course.objects.get(projects=project)
        # Get the members to add, as a list
        members = request.POST.getlist('members')
        # current members of the project
        curr_members = Membership.objects.filter(project=project)
        added = False
        # send requests to members
        for uname in members:
            mem_to_add = User.objects.get(username=uname)
            mem_courses = Course.get_my_courses(mem_to_add)
            # Don't add a member if they already have membership in project
            # Confirm that the member is a part of the course
            # List comprehenshion: loops through this projects memberships in order
            #   to check if mem_to_add is in the user field of a current membership.
            if this_course in mem_courses and mem_to_add not in [mem.user for mem in curr_members]:
                # add user to pending invitations
                project.pending_invitations.add(mem_to_add)
                project.save()

                # send user an alert
                Alert.objects.create(
                    sender=request.user,
                    to=mem_to_add,
                    msg="You have been invited to join the Project: " + project.title,
                    url=reverse('view_one_project',args=[project.slug]),
                    alertType="invitation",
                    slug=project.slug
                    )

                # send user an email
                subject = "GrepThink Project Invitation: " + project.title
                content = "You have been invited to Join the Project: {0},\n\n You can accept this invitation from the alerts dropdown in the topright @ grepthink.com".format(project.title)

                send_email(mem_to_add, request.user.email, subject, content)
                added = True

        if added:
            messages.add_message(request, messages.SUCCESS, "Greppers have been invited to join your project!")
        else:
            messages.add_message(request, messages.WARNING, "Failed to invite member(s) to project")
        return redirect(view_one_project, project.slug)

    # Remove a user from the project
    if request.POST.get('remove_user'):
        f_username = request.POST.get('remove_user')
        f_user = User.objects.get(username=f_username)
        to_delete = Membership.objects.filter(user=f_user, project=project)

        remaining = Membership.objects.filter(project=project).exclude(user=f_user)

        # check if they were the only member of the project
        if len(members) == 1:
            messages.warning(request,
             "As the only member of the project, you must invite another to be the Project Owner, or delete the project via Edit Project!")
        else:
            # check if user that is being removed was Project Owner
            if f_user == project.creator:
                project.creator = remaining.first().user
            # check if user that is being removed was Scrum Master
            if f_user == project.scrum_master:
                project.scrum_master = remaining.first().user

            project.save()
            messages.info(request, "{0} has been removed from the project".format(f_username))

            # delete membership
            for mem_obj in to_delete:
                mem_obj.delete()

        return redirect(view_one_project, project.slug)


    # Transfer ownership of a project
    if request.POST.get('promote_user'):
        f_username = request.POST.get('promote_user')
        f_user = User.objects.get(username=f_username)

        if request.user == project.creator:
            project.creator = f_user
            project.save()
            messages.info(request, "{0} is now the Project Owner".format(f_username))
        else:
            messages.warning(request,'Only the current Project Owner can give away Project Ownership.')

        return redirect(edit_project, slug)

    # Transfer Scrum Master
    if request.POST.get('make_scrum'):
        f_username = request.POST.get('make_scrum')
        f_user = User.objects.get(username=f_username)
        project.scrum_master = f_user
        project.save()
        messages.info(request, "{0} is now the Scrum Master".format(f_username))
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
        return redirect(view_one_project, project.slug)

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
            project.project_image = form.cleaned_data.get('project_image')
            project.ta_time = form.cleaned_data.get('ta_time')
            project.ta_location = form.cleaned_data.get('ta_location')
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
        'page_description': page_description, 'title' : title, 'members':members,
        'form': form, 'project': project, 'user':request.user})


@login_required
def post_update(request, slug):
    """
    Post an update for a given project
    """
    project = get_object_or_404(Project, slug=slug)

    if request.user.profile.isGT:
        pass
    elif not request.user == project.creator and request.user not in project.members.all(
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

    if request.user.profile.isGT:
        pass
    elif not request.user == project.creator and request.user not in project.members.all(
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

    return render(request, 'projects/add_resource.html', {'form': form, 'project': project})

def populate_tsr_forms(request, emails, members, scrum_master):
    """
    Private helper function that takes a request, emails, members, and scrum_master
    variables to populate the tsr_forms based on the member's email.
    """
    tsr_forms = list()
    for member_email in emails:
        form_iterator = TSR(request.user.id, request.POST, members=members,
                            emails=emails, prefix=member_email, scrum_master=scrum_master)
        tsr_forms.append(form_iterator)
    return tsr_forms

@login_required
def tsr_update(request, slug, assslug):
    """
    public method that takes in a slug and generates a TSR
    form for user. Different form generated based on which
    button was pressed (scrum/normal)
    """
    page_name = "TSR Update"
    page_description = "Update TSR form"
    title = "TSR Update"

    user = request.user
    cur_proj = get_object_or_404(Project, slug=slug)
    asg = get_object_or_404(Assignment, slug=assslug)
    today = datetime.now().date()
    members = cur_proj.members.all()
    emails = list()
    for member in members:
        emails.append(member.email)

    if cur_proj.scrum_master == user:
        scrum_master = True
    else:
        scrum_master = False

    late = False

    asg_ass_date = asg.ass_date

    asg_due_date = asg.due_date
    if asg_ass_date <= today <= asg_due_date:
        late = False
    else:
        late = True
    print(late)

    tsr_forms = list()
    if request.method == 'POST':
        percent_addup = 0
        for email in emails:
            # grab form
            form = TSR(request.user.id, request.POST, members=members,
                       emails=emails, prefix=email, scrum_master=scrum_master)
            if form.is_valid():
                tsr = Tsr()
                tsr.ass_number = asg.ass_number
                tsr.percent_contribution = form.cleaned_data.get('perc_contribution')
                percent_addup += tsr.percent_contribution
                tsr.positive_feedback = form.cleaned_data.get('pos_fb')
                tsr.negative_feedback = form.cleaned_data.get('neg_fb')
                tsr.tasks_completed = form.cleaned_data.get('tasks_comp')
                tsr.performance_assessment = form.cleaned_data.get('perf_assess')
                tsr.notes = form.cleaned_data.get('notes')
                tsr.evaluator = request.user
                tsr.evaluatee = User.objects.filter(email__iexact=email).first()
                tsr.late = late
                print(tsr.late)

                tsr.save()
                tsr_forms.append(tsr)

        if len(emails) != 1 and percent_addup != 100:
            messages.error(request, "Contribution does not add up to 100%. Please try again.")

            tsr_forms = populate_tsr_forms(request, emails, members, scrum_master)
            form = TSR(request.user.id, request.POST, members=members,
                       emails=emails, scrum_master=scrum_master)
            return render(request, 'projects/tsr_update.html',
                          {'forms':tsr_forms, 'cur_proj': cur_proj, 'ass':asg,
                           'page_name' : page_name, 'page_description': page_description,
                           'title': title, 'scrum_master_form':'scrum_master_form'})
        else:
            for tsr in tsr_forms:
                # gets fields variables and saves them to project
                cur_proj.tsr.add(tsr)
                cur_proj.save()
                asg.subs.add(tsr)
                asg.save()

        return redirect(view_one_project, slug)

    else:
        # if request was not post then display tsr_forms
        tsr_forms = populate_tsr_forms(request, emails, members, scrum_master)

    return render(request, 'projects/tsr_update.html',
                  {'forms':tsr_forms, 'cur_proj':cur_proj, 'ass':asg,
                   'page_name':page_name, 'page_description':page_description,
                   'title':title})

@login_required
def tsr_edit(request, slug, assslug):
    """
    public method that takes in a slug and generates a TSR
    form for user. Different form generated based on which
    button was pressed (scrum/normal)
    """
    page_name = "TSR Edit"
    page_description = "Edit TSR form"
    title = "TSR Edit"

    user = request.user
    cur_proj = get_object_or_404(Project, slug=slug)
    course = Course.objects.get(projects=cur_proj)
    asg = get_object_or_404(Assignment, slug=assslug)
    today = datetime.now().date()
    members = cur_proj.members.all()
    emails = list()
    for member in members:
        emails.append(member.email)

    params = str(request)
    if "scrum_master_form" in params:
        scrum_master = True
    else:
        scrum_master = False

    late = False
    if "tsr" in asg.ass_type.lower():
        asg_ass_date = asg.ass_date
        asg_ass_date = datetime.strptime(asg_ass_date,"%Y-%m-%d").date()

        asg_due_date = asg.due_date
        asg_due_date = datetime.strptime(asg_due_date,"%Y-%m-%d").date()
        if asg_ass_date <= today <= asg_due_date:
            late = False
        else:
            late=True

    forms =list()
    if request.method == 'POST':
        for email in emails:
            # grab form
            form = TSR(request.user.id, request.POST, members=members,
                emails=emails, prefix=email, scrum_master=scrum_master)
            if form.is_valid():
                tsr = Tsr()
                tsr.ass_number = asg.ass_number
                tsr.percent_contribution = form.cleaned_data.get('perc_contribution')
                tsr.positive_feedback = form.cleaned_data.get('pos_fb')
                tsr.negative_feedback = form.cleaned_data.get('neg_fb')
                tsr.tasks_completed = form.cleaned_data.get('tasks_comp')
                tsr.performance_assessment = form.cleaned_data.get('perf_assess')
                tsr.notes = form.cleaned_data.get('notes')
                tsr.evaluator = request.user
                tsr.evaluatee =  User.objects.filter(email__iexact=email).first()
                tsr.late = late

                tsr.save()

                # gets fields variables and saves them to project
                cur_proj.tsr.add(tsr)
                cur_proj.save()
                asg.subs.add(tsr)
                asg.save()

        return redirect(view_one_project, slug)

    else:
        # if request was not post then display forms
        for m in emails:
            form_i=TSR(request.user.id, request.POST, members=members,
             emails=emails, prefix=m, scrum_master=scrum_master)
            forms.append(form_i)
        form = TSR(request.user.id, request.POST, members=members,
            emails=emails, scrum_master=scrum_master)

    return render(request, 'projects/tsr_update.html',
    {'forms':forms,'cur_proj': cur_proj, 'ass':asg,
    'page_name' : page_name, 'page_description': page_description,
    'title': title})

@login_required
def view_tsr(request, slug):
    """
    public method that takes in a slug and generates a view for
    submitted TSRs
    """
    page_name = "View TSR"
    page_description = "Submissions"
    title = "View TSR"
    project = get_object_or_404(Project, slug=slug)
    tsrs = list(project.tsr.all())
    members = project.members.all()

	
    # put emails into list
    emails=list()
    for member in members:
        emails.append(member.email)

    # for every sprint, get the tsr's and calculate the average % contribution
    tsr_dicts=list()
    tsr_dict = list()
    sprint_numbers=Tsr.objects.values_list('ass_number',flat=True).distinct()
    for i in sprint_numbers.all():
        #averages=list()
        tsr_dict = list()
        for member in members:
            tsr_single = list()
            # for every member in project, filter query using member.id
            # and assignment number
            for member_ in members:
                if member == member_:
                    continue
                tsr_query_result = Tsr.objects.filter(evaluatee_id=member.id).filter(evaluator_id=member_.id).filter(ass_number=i).all()
                if(len(tsr_query_result)==0):
                    continue
                tsr_single.append(tsr_query_result[len(tsr_query_result)-1])
            avg=0
            if(len(tsr_single)!=0):
                for tsr_obj in tsr_single:
                    print("\n\n%d\n\n"%tsr_obj.percent_contribution)
                    avg=avg+tsr_obj.percent_contribution
                avg=avg/len(tsr_single)
            tsr_dict.append({'email':member.email, 'tsr' :tsr_single,
                'avg' : avg})
            averages.append({'email':member.email,'avg':avg})
        tsr_dicts.append({'number': i , 'dict':tsr_dict,
            'averages':averages})

    med = 1
    if len(members):
        med = int(100/len(members))
    mid = {'low' : int(med*0.7), 'high' : int(med*1.4)}


    if request.method == 'POST':

        return redirect(view_projects)
    
    return render(request, 'projects/view_tsr.html', {'page_name' : page_name, 'page_description': page_description, 'title': title, 'tsrs' : tsr_dicts, 'contribute_levels' : mid, 'avg':averages})



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

def add_member(request, slug, uname):
    """
    Add member to project if:
        - They aren't a member already
        - They are a member of the course
    """
    project = get_object_or_404(Project, slug=slug)
    course = Course.objects.get(projects=project)
    mem_to_add = User.objects.get(username=uname)
    mem_courses = Course.get_my_courses(mem_to_add)
    curr_members = Membership.objects.filter(project=project)

    # ensure user is a member of the course && not a member of the project
    if course in mem_courses and mem_to_add not in [mem.user for mem in curr_members]:
        Membership.objects.create(
            user=mem_to_add, project=project, invite_reason='')
        Alert.objects.create(
            sender=request.user,
            to=mem_to_add,
            msg="You were added to " + project.title,
            url=reverse('view_one_project',args=[project.slug]),
            )
        # remove member from pending list if he/she was on it
        pending_members = project.pending_members.all()
        if mem_to_add in pending_members:
            for mem in pending_members:
                if mem == mem_to_add:
                    project.pending_members.remove(mem)
                    project.save()

    # taken from alert code
    user = request.user
    profile = Profile.objects.get(user=user)
    unread = profile.unread_alerts()
    for alert in unread:
        if alert.slug == project.slug:
            if alert.to.id is user.id:
                alert.read = True
                alert.save()

    return redirect(view_one_project, slug)

def reject_member(request, slug, uname):
    """
    Reject Membership
    """
    project = get_object_or_404(Project, slug=slug)
    mem_to_add = User.objects.get(username=uname)

    # remove member from pending list if he/she was on it
    pending_members = project.pending_members.all()
    if mem_to_add in pending_members:
        for mem in pending_members:
            if mem == mem_to_add:
                project.pending_members.remove(mem)
                project.save()

        Alert.objects.create(
            sender=request.user,
            to=mem_to_add,
            msg="Sorry, " + project.title + " has denied your request",
            url=reverse('view_one_project',args=[project.slug]),
            )

    # taken from alert code
    user = request.user
    profile = Profile.objects.get(user=user)
    unread = profile.unread_alerts()
    for alert in unread:
        if alert.slug == project.slug:
            if alert.to.id is user.id:
                alert.read = True
                alert.save()
                return redirect(view_alerts)

    return redirect(view_one_project, slug)

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

            # attachment = request.FILES['attachment']
            # if attachment:
            #     handle_file(attachment)

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

    
def similarity_of_eval_history(project, asgn_number):
    """
    Helper function that returns a dictionary of dictionaries
    reporting if each teammate's evaluations for team members are similar across all TSRs.
    """
    historic_similarities = {}
    members = project.members.all()
    marginofsimilarity = decimal.Decimal(0.1)


    for current_evaluator in members:
        evaluator_similarities = {}
        
        for current_evaluatee in members:
            evaluator_tsrs = list(project.tsr.all().filter(evaluatee=current_evaluatee, evaluator=current_evaluator))
            average_evaluation = 0
            num_evals_considered = 0
            for evaluation in evaluator_tsrs:
                if evaluation.ass_number <= asgn_number:
                    average_evaluation += evaluation.percent_contribution
                    num_evals_considered += 1
            
            average_evaluation /= num_evals_considered
            upper_bound = math.ceil(average_evaluation + (average_evaluation * marginofsimilarity))
            lower_bound = math.floor(average_evaluation - (average_evaluation * marginofsimilarity))

            for evaluation in evaluator_tsrs:
                if evaluation.ass_number <= asgn_number:
                    if lower_bound <= evaluation.percent_contribution <= upper_bound:
                        evaluator_similarities[current_evaluatee] = True
                    else:
                        evaluator_similarities[current_evaluatee] = False
        historic_similarities[current_evaluator] = evaluator_similarities
    for member in historic_similarities:
        hist_similar_count = 0
        #preconditions:(project , ([int]tsr_number, [User]associated_member , [string]analysis_type, [string]analysis_output))
        analysis_data = (asgn_number, member, "Historically Similar Scores", historic_similarities[member])
        analysis_object = setAnalysisData(project, analysis_data)
        
        for evaluatee in historic_similarities[member]:
            if historic_similarities[member][evaluatee] == True:
                hist_similar_count += 1

        #preconditions:( AnalysisObject, ([boolean] flag_tripped, [String]flag_detail))
        if hist_similar_count > 0:
            setFlag(analysis_object, (True, "%s has given %d sets of similar scores over time." % (member, hist_similar_count)))
    return historic_similarities
    
def giving_outlier_scores(project, asgn_number):
    """
    Helper function that returns a dictionary of dictionaries of (member, low/high) pairs keyed
    to evaluator.
    """
    outlier_scores = {}
    members = project.members.all()
    low_bound, high_bound = ideal_score_ranges(project)
    for current_evaluator in members:
        evaluator_tsrs = list(project.tsr.all().filter(ass_number=asgn_number, evaluator=current_evaluator))
        evaluator_outliers = {}
        for evaluation in evaluator_tsrs:
            evaluatee = evaluation.evaluatee
            if evaluation.percent_contribution <= low_bound:
                evaluator_outliers[evaluatee] = 'Low'
            elif evaluation.percent_contribution >= high_bound:
                evaluator_outliers[evaluatee] = 'High'
        outlier_scores[current_evaluator] = evaluator_outliers
    
    for member in outlier_scores:
        low_count = 0
        high_count = 0
        #preconditions:(project , ([int]tsr_number, [User]associated_member , [string]analysis_type, [string]analysis_output))
        analysis_data = (asgn_number, member, "Outlier Scores", outlier_scores[member])
        analysis_object = setAnalysisData(project, analysis_data)
        
        for evaluatee in outlier_scores[member]:
            if outlier_scores[member][evaluatee] == 'Low':
                low_count += 1
            elif outlier_scores[member][evaluatee] == 'High':
                high_count += 1
        #preconditions:( AnalysisObject, ([boolean] flag_tripped, [String]flag_detail))
        if high_count > 0 or low_count > 0:
            setFlag(analysis_object, (True, "%s has given %d very low scores and %d very high scores." % (member, low_count, high_count)))
       
    return outlier_scores
    
def ideal_score_ranges(project):
    members = project.members.all()
    ideal_average = math.floor(100/len(members))
    outlier_percentage = decimal.Decimal(0.5)
    low_bound = math.floor(ideal_average - (ideal_average * outlier_percentage))
    high_bound = math.ceil(ideal_average + (ideal_average * outlier_percentage))
    return (low_bound, high_bound)

def tsr_word_count(project, asgn_number):
    """
    Helper function that returns a dictionary of dictionaries of dictionaries of (pos/neg feedback, word count) pairs keyed
    to evaluatee keyed to evaluator.
    """
    word_counts = {}
    members = project.members.all()
    sparse_limit = 5
    verbose_limit = 20
    
    for current_evaluator in members:
        evaluator_tsrs = list(project.tsr.all().filter(ass_number=asgn_number, evaluator=current_evaluator))
        evaluator_word_counts = {}
        for evaluation in evaluator_tsrs:
            evaluatee = evaluation.evaluatee
            feedback_lengths = {}
            pos_feedback = evaluation.positive_feedback.split(None)
            neg_feedback = evaluation.negative_feedback.split(None)
            feedback_lengths['pos_feedback'] = len(pos_feedback)
            feedback_lengths['neg_feedback'] = len(neg_feedback)
            evaluator_word_counts[evaluatee] = feedback_lengths
        word_counts[current_evaluator] = evaluator_word_counts 
		
		                    
    for member in word_counts:
        #preconditions:(project , ([int]tsr_number, [User]associated_member , [string]analysis_type, [string]analysis_output))
        analysis_data = (asgn_number, member, "Word Count", word_counts[member])
        analysis_object = setAnalysisData(project, analysis_data)
        sparse_count = 0
        verbose_count = 0
        
        for evaluatee in word_counts[member]:
            sparse_test = 0
            verbose_test = 0
            for feedback_type in word_counts[member][evaluatee]:
                if word_counts[member][evaluatee][feedback_type] < sparse_limit:
                    sparse_test += 1
                elif word_counts[member][evaluatee][feedback_type] > verbose_limit:
                    verbose_test += 1
            if sparse_test == 2:
                sparse_count += 1
            elif verbose_test > 1:
                verbose_count += 1
                
        if sparse_count > 0 or verbose_count > 0:
            setFlag(analysis_object, (True, "%s has given %d sparse responses and %d verbose responses." % (member, sparse_count, verbose_count)))
		
    return word_counts

def has_atleast_one_identical(member, total_report):
    for name in total_report:
        tuple_result = total_report[member][name]
        if tuple_result[0]:
            return True
    return False

def similarity_for_given_evals(project, asgn_number):
    """
    Helper function that returns a dictionary of dictionaries
    reporting if each teammate's evaluations of him/herself and others 
    are similar across a range of particular TSRs.
    """
    all_similarities = {}
    members = project.members.all()
    marginofsimilarity = decimal.Decimal(0.1)

    for current_evaluator in members:
        evaluator_tsrs = list(project.tsr.all().filter(ass_number=asgn_number, evaluator=current_evaluator))
        evaluator_similarities = {}
        average_contribution = 0

        for evaluation in evaluator_tsrs:
            average_contribution += evaluation.percent_contribution
        average_contribution /= len(members)
        upper_bound = math.ceil(average_contribution + (average_contribution * marginofsimilarity))
        lower_bound = math.floor(average_contribution - (average_contribution * marginofsimilarity))

        for evaluation in evaluator_tsrs:
            evaluatee = evaluation.evaluatee
            if lower_bound <= evaluation.percent_contribution <= upper_bound:
                evaluator_similarities[evaluatee] = (True, evaluation.percent_contribution)
            else:
                evaluator_similarities[evaluatee] = (False, evaluation.percent_contribution)
        all_similarities[current_evaluator] = evaluator_similarities

    for member in all_similarities:
        analysis_data = (asgn_number, member, "Similarity for Given Evaluations",
                         all_similarities[member])
        analysis_flags = (has_atleast_one_identical(member, all_similarities),
                          "%s has been giving very similar scores to other team members." % member)
        analysis_object = setAnalysisData(project, analysis_data)
        setFlag(analysis_object, analysis_flags)
    return all_similarities

def averages_for_all_evals(project, asgn_number):
    """
    Helper function that returns a dictionary of averages for percent
    contributions for each team member in a project.
    """
    member_averages = {}
    members = project.members.all()

    for current_evaluatee in members:
        evaluatee_tsrs = list(project.tsr.all().filter(evaluatee=current_evaluatee))
        average_contribution = 0
        num_evals_considered = 0
        for evaluation in evaluatee_tsrs:
            if evaluation.ass_number <= asgn_number:
                average_contribution += evaluation.percent_contribution
                num_evals_considered += 1
             
        bounds = ideal_score_ranges(project)
        member_averages[current_evaluatee] = round(average_contribution / num_evals_considered, 1)
        analysis_data = (asgn_number, current_evaluatee, "Averages for all Evaluations",
                         member_averages[current_evaluatee])
        analysis_object = setAnalysisData(project, analysis_data)
        # bounds[1] is the high bound.
        if member_averages[current_evaluatee] >= bounds[1]:
            analysis_flag = (True,
                             "%s has a higher than typical average score." % current_evaluatee)
            setFlag(analysis_object, analysis_flag)
        # bounds[0] is the low bound.
        elif member_averages[current_evaluatee] <= bounds[0]:
            analysis_flag = (False,
                             "%s has a lower than typical average score." % current_evaluatee)
            setFlag(analysis_object, analysis_flag)
    return member_averages
    
#the wrapper function : gets current project and data and saves it to correct project
#preconditions:(project , ([int]tsr_number, [User]associated_member , [string]analysis_type, [string]analysis_output)
def setAnalysisData(project, analysisData):
    analysis = Analysis()
    analysis.tsr_number = analysisData[0]
    analysis.associated_member = analysisData[1]
    analysis.analysis_type = analysisData[2]
    analysis.analysis_output = analysisData[3]
    analysis.save()
                 
    #saving in manytomany field project
    project.analysis.add(analysis)
    project.save()

    return analysis


#the wrapper function :updates the piece of analysis with the correct flag information
#preconditions:( AnalysisObject, ([boolean] flag_tripped, [String]flag_detail))
def setFlag(analysis_object, flag_info):
    analysis_object.flag_tripped = flag_info[0]
    analysis_object.flag_detail = flag_info[1]
    analysis_object.save()

