# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

# Models
from teamwork.apps.core.models import *
from teamwork.apps.courses.models import *

# form
from teamwork.apps.projects.forms import *

# redirect views
from teamwork.apps.projects.views.ProjectView import view_one_project

# Helpers
from teamwork.apps.projects.views.BaseView import *
from teamwork.apps.core.helpers import *

@login_required
def edit_project(request, slug):
    """
    Public method that serves the form allowing a user to edit a project
    Based off courses/views.py/edit_course
    """
    project = get_object_or_404(Project.objects.prefetch_related('members', 'course').select_related('creator'), slug=slug)
    course = project.course.first()
    project_owner = project.creator.profile
    members = project.members.all()

    # Populate page info with edit project title/name
    page_name = "Edit Project"
    page_description = "Make changes to " + project.title
    title = "Edit Project"

    user_role = get_user_role(request.user, course)

    # if user is not project owner or they arent in the member list
    if request.user.profile.isGT or request.user == course.creator or user_role == "ta":
        pass
    elif not request.user  in project.members.all():
        #redirect them with a message
        messages.warning(request, 'Only the Project Owner can make changes to this project!')
        return redirect(view_one_project, project.slug)

    if request.POST.get('delete_project'):
        print("deleting project")
        # Rights: GT, Professor, TA, Project Creator
        if request.user == project.creator or request.user == course.creator or request.user.profile.isGT or user_role == "ta":
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
        profAdded = False

        # send requests to members
        for uname in members:
            mem_to_add = User.objects.get(username=uname)
            mem_courses = Course.get_my_courses(mem_to_add)

            # Don't add a member if they already have membership in project
            # Confirm that the member is a part of the course
            # List comprehenshion: loops through this projects memberships in order
            #   to check if mem_to_add is in the user field of a current membership.
            if this_course in mem_courses and mem_to_add not in [mem.user for mem in curr_members]:
                if request.user == course.creator:
                    # if the professor of the course wants to add members to a project, just add them
                    success = add_member(request, slug, uname)

                    if success:
                        # send user that was added an email
                        subject = "You've been added to a Project"
                        content = "You have been added to the Project: {0}.\n\n".format(project.title)
                        send_email(mem_to_add, request.user.email, subject, content)

                        # profAdded bool used to give the correct Success Message
                        profAdded = True
                else:
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
        elif this_course in mem_courses and mem_to_add not in [mem.user for mem in curr_members]:
            messages.add_message(request, messages.SUCCESS, "Grepper(s) have been added to the project.")
        else:
            if (not course in mem_courses):
                messages.warning(request, "User failed to be added to the project. " + mem_to_add.username + " is not enrolled in the course")
            else:
                messages.add_message(request, messages.WARNING, "Student(s) is already added to the project.") 

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


    # Transfer ownership of a project - TODO: needs to be removed, but add messages to new implementation
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

    # Transfer Scrum Master  - TODO: needs to be removed, but add messages to new implementation
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
#-----------------------------------------------------------------
    if request.POST.get('desired_techs'):
        techs = request.POST.getlist('desired_techs')
        for s in techs:
            s_lower = s.lower()
            # Check if lowercase version of skill is in db
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
        return redirect(view_one_project, project.slug)

    if request.POST.get('remove_desired_tech'):
        tech_name = request.POST.get('remove_desired_tech')
        to_delete = Techs.objects.get(tech=tech_name)
        project.desired_techs.remove(to_delete)
        return redirect(edit_project, slug)
#-----------------------------------------------------------------
    if request.method == 'POST':
        form = EditProjectForm(request.user.id, request.POST, members=members)

        if form.is_valid():
            # edit the project object, omitting slug
            project.title = form.cleaned_data.get('title')
            project.tagline = form.cleaned_data.get('tagline')
            project.avail_mem = form.cleaned_data.get('accepting')
            project.sponsor = form.cleaned_data.get('sponsor')
            project.teamSize = form.cleaned_data.get('teamSize')
            project.no_request = form.cleaned_data.get('no_request')
            project.weigh_interest = form.cleaned_data.get('weigh_interest') or 0
            project.weigh_know = form.cleaned_data.get('weigh_know') or 0
            project.weigh_learn = form.cleaned_data.get('weigh_learn') or 0
            project.project_image = form.cleaned_data.get('project_image')
            project.ta_time = form.cleaned_data.get('ta_time')
            project.ta_location = form.cleaned_data.get('ta_location')

            # roles
            if form.cleaned_data.get('project_owner'):
                project.creator = form.cleaned_data.get('project_owner')

            if form.cleaned_data.get('scrum_master'):
                project.scrum_master = form.cleaned_data.get('scrum_master')

            # Project content
            project.content = form.cleaned_data.get('content')
            project.lower_time_bound = form.cleaned_data.get('lower_time_bound')
            project.upper_time_bound = form.cleaned_data.get('upper_time_bound')

            project.save()

            # Not sure if view_one_project redirect will work...
            return redirect(view_one_project, project.slug)
    else:
        form = EditProjectForm(request.user.id, instance=project, members=members)

        # TEMPORARILIY COMMENTED OUT, DUE TO JULLIG HAVING TROUBLE ADDING MEMBERS
        # if members:
        #     form.fields['project_owner'].required = True
        #     form.fields['scrum_master'].required = True

    return render(request, 'projects/edit_project.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title, 'members':members,
        'form': form, 'project': project, 'user':request.user})

def try_add_member(request, slug, uname):
    """
    Add member to project if:
        - They aren't a member already
        - They are a member of the course
        - The project is still accepting members
    """
    project = get_object_or_404(Project.objects.prefetch_related('course', 'members', 'pending_members'), slug=slug)
    course = project.course.first()

    mem_to_add = User.objects.get(username=uname)
    mem_courses = Course.get_my_courses(mem_to_add)
    curr_members = project.members.all()

    # ensure user is a member of the course && not a member of the project
    if user_can_be_added(request, project, course, mem_to_add, mem_courses, curr_members):
        add_member(request, slug, uname)

    return redirect(view_one_project, slug)

def add_member(request, slug, uname):
    """
    Add a member to a project.
    - Project grabbed using slug
    - User grabbed using username
    """

    project = get_object_or_404(Project, slug=slug)
    mem_to_add = User.objects.get(username=uname)

    Membership.objects.create(
        user=mem_to_add, project=project, invite_reason='')
    Alert.objects.create(
        sender=request.user,
        to=mem_to_add,
        msg="You were added to " + project.title,
        url=reverse('view_one_project',args=[project.slug]),
        )

    adjust_pendinglist(request, project, mem_to_add)

def adjust_pendinglist(request, project, mem_to_add):
    """
    Removes mem_to_add from the projects pending_members list if they are on there.
    Creates an alert to notify the user that they were added to a project.

    """
    # remove member from pending list if he/she was on it
    pending_members = project.pending_members.all()
    if mem_to_add in pending_members:
        for mem in pending_members: #TODO: probably a better more python way to remove this item from list
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

def user_can_be_added(request, project, course, mem_to_add, mem_courses, curr_members):

    if (not course in mem_courses):
        messages.warning(request, "User failed to be added to the project. " + mem_to_add.username + " is not enrolled in the course")
        return False

    if (mem_to_add in curr_members):
        messages.warning(request, "User failed to be added to the project. " + mem_to_add.username + " is already a member of the project.")
        return False

    if not project.avail_mem:
        messages.warning(request, "Project: " + project.title + " is not currently accepting members.")
        return False

    return True

def leave_project(request, slug):
    """
    Called only diretly from template. EditProjectForm has 'Leave Project' option for yourself.
    """
    project = get_object_or_404(Project.objects.prefetch_related('members', 'pending_members').select_related('creator', 'scrum_master'), slug=slug)
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
#--------------------------------------------------------------------------
def add_desired_techs(request, slug):
    if request.method == 'GET' and request.is_ajax():
        # JSON prefers dictionaries over lists.
        data = dict()
        # A list in a dictionary, accessed in select2 ajax
        data['items'] = []
        q = request.GET.get('q')
        if q is not None:
            results = Techs.objects.filter(
                Q( tech__contains = q ) ).order_by( 'tech' )
        for s in results:
            data['items'].append({'id': s.tech, 'text': s.tech})
        return JsonResponse(data)

def create_desired_techs(request):
    if request.method == 'GET' and request.is_ajax():
        # JSON prefers dictionaries over lists.
        data = dict()
        # A list in a dictionary, accessed in select2 ajax
        data['items'] = []
        q = request.GET.get('q')
        if q is not None:
            results = Techs.objects.filter(
                Q( tech__contains = q ) ).order_by( 'tech' )
        for s in results:
            data['items'].append({'id': s.tech, 'text': s.tech})
        return JsonResponse(data)

def edit_techs(request, username):
    if request.method == 'GET' and request.is_ajax():
        # JSON prefers dictionaries over lists.
        data = dict()
        # A list in a dictionary, accessed in select2 ajax
        data['items'] = []
        q = request.GET.get('q')
        if q is not None:
            results = Techs.objects.filter(
                Q( tech__contains = q ) ).order_by( 'tech' )
        for s in results:
            data['items'].append({'id': s.tech, 'text': s.tech})
        return JsonResponse(data)


    return HttpResponse("Failure")

#--------------------------------------------------------------------------
    return HttpResponse("Failure")
