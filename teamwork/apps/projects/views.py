from .models import *
from .forms import *

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest,  HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from teamwork.apps.courses.models import *


from teamwork.apps.core.models import *

def _projects(request, projects):
    """
    Private method that will be used for paginator once I figure out how to get it working.
    """
    page = request.GET.get('page')

    return render(request, 'projects/view_projects.html',
            {'projects': projects}
        )

@login_required
def view_projects(request):
    """
    Public method that takes a request, retrieves all Project objects from the model,
    then calls _projects to render the request to template view_projects.html
    """
    my_projects = Project.get_my_projects(request.user)
    my_created = Project.get_created_projects(request.user)
    projects = my_projects | my_created
    return _projects(request, projects)


@login_required
def view_one_project(request, slug):
    """
    Public method that takes a request and a projecttitle, retrieves the Project object from the model
    with given projecttitle.  Renders projects/view_project.html
    # TODO: fix up return calls
    """
    project = get_object_or_404(Project, slug=slug)
    updates = project.get_updates()

    matches = POMatch(project)

    return render(request, 'projects/view_project.html', {
        'project': project , 'updates' :updates
        })

@login_required
def create_project(request):
    """
    Public method that creates a form and renders the request to create_project.html
    """
    user_id = request.user.id
    user = Profile.objects.get(user=user_id)
    #enrollment objects containing current user
    enroll = Enrollment.objects.filter(user=request.user)
    #current courses user is in
    cur_courses = Course.objects.filter(enrollment__in=enroll)
    no_postable_classes = False

    my_created_courses = Course.objects.filter(creator=request.user.username)
    #If user is in 0 courses
    if len(enroll) == 0 and len(my_created_courses) == 0:
            #Redirect them to homepage and tell them to join a course
            messages.info(request,'You need to join a course before creating projects!')
            return HttpResponseRedirect('/')


    if len(cur_courses) == len(cur_courses.filter(limit_creation=True)):
        no_postable_classes = True

    if len(enroll) >= 1 and no_postable_classes and not user.isProf:
            #Redirect them to homepage and tell them to join a course
            messages.info(request,'Professor has disabled Project Creation!')
            return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = ProjectForm(request.user.id, request.POST)
        if form.is_valid():
            # create an object for the input
            project = Project()
            # Project slug
            project.slug = form.cleaned_data.get('slug')
            project.title = form.cleaned_data.get('title')
            project.creator = request.user.username
            project.avail_mem = form.cleaned_data.get('accepting')
            project.sponsor = form.cleaned_data.get('sponsor')

            project.save()

            # Handle desired skills
            desired = form.cleaned_data.get('desired_skills')
            if desired:
                # parse known on ','
                skill_array = desired.split(',')
                for skill in skill_array:
                    stripped_skill = skill.strip()
                    if not (stripped_skill == ""):
                        # check if skill is in Skills table, lower standardizes input
                        if Skills.objects.filter(skill=stripped_skill.lower()):
                            # skill already exists, then pull it up
                            desired_skill = Skills.objects.get(skill=stripped_skill.lower())
                        else:
                            # we have to add the skill to the table
                            desired_skill = Skills.objects.create(skill=stripped_skill.lower())
                            # save the new object
                            desired_skill.save()
                        # This is how we can use the reverse of the relationship
                        print("\n\n")
                        print(desired_skill.desired.all())
                        print("\n\n")
                        # add the skill to the current profile
                        project.desired_skills.add(desired_skill)
                        project.save() #taking profile.save() out of these if's and outside lets all the changes be saved at once
                        # This is how we can get all the skills from a user
                        print("\n\n")
                        print(project.desired_skills.all())
                        print("\n\n")
            # Project content
            project.content = form.cleaned_data.get('content')

            # Local list of memebers, used to create Membership objects
            members = form.cleaned_data.get('members')

            project.save()

            in_course = form.cleaned_data.get('course')
            in_course.projects.add(project)

            # loop through the members in the object and make m2m rows for them
            for i in members:
                Membership.objects.create(user=i.user, project=project, invite_reason='')

            # if user is not a prof
            if not user.isProf:
                Membership.objects.create(user=user.user, project=project, invite_reason='')

            # we dont have to save again because we do not touch the project object
            # we are doing behind the scenes stuff (waves hand)
            return redirect(view_projects)
    else:
        form = ProjectForm(request.user.id)
    return render(request, 'projects/create_project.html', {'form': form})

@login_required
def edit_project(request, slug):
    """
    Public method that serves the form allowing a user to edit a project
    Based off courses/views.py/edit_course
    """

    #WARNING 3/7 PROJECTS MAY NOT BE UPDATING
    project = get_object_or_404(Project, slug=slug)

    # if user is not project owner or they arent in the member list
    if not request.user.username == project.creator and request.user not in project.members.all():
        #redirect them with a message
        messages.info(request,'Only Project Owner can edit project!')
        return HttpResponseRedirect('/project/all')

    if request.method == 'POST':
        form = ProjectForm(request.user.id, request.POST)
        if form.is_valid():
            # edit the project object, omitting slug
            project.title = form.cleaned_data.get('title')
            project.avail_mem = form.cleaned_data.get('accepting')
            project.sponsor = form.cleaned_data.get('sponsor')
            project.save()

            members = form.cleaned_data.get('members')


            # Clear all memberships to avoid duplicates.
            memberships = Membership.objects.filter(project=project)
            if memberships is not None: memberships.delete()
            for i in members:
                Membership.objects.create(user=i.user, project=project, invite_reason='')

            # Not sure if view_one_project redirect will work...
            return redirect(view_one_project, project.slug)
    else:
        form = ProjectForm(request.user.id, instance=project)
    return render(
            request, 'projects/edit_project.html',
            {'form': form,'project': project}
            )

@login_required
def delete_project(request, slug):
    """
    Delete project method
    """
    project = get_object_or_404(Project, slug=slug)

    ## Do something to check that the current user is the project owner
    # if not request.user.id == project.owner.id:
    #     return redirect(view_one_project, project.slug)
    # else:
    #     project.delete()
    #     return redirect(view_projects)

    project.delete()
    return redirect(view_projects)

@login_required
def post_update(request, slug):
    """
    Post an update for a given project
    """
    project = get_object_or_404(Project, slug=slug)

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
    return render(request, 'projects/post_update.html', {'form': form, 'project': project})
