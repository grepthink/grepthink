from .models import *
from .forms import *

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest,  HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

def _projects(request, projects):
    """
    Private method that will be used for paginator once I figure out how to get it working.
    """
    #paginator = Paginator(projects, 10)
    page = request.GET.get('page')
    #try:
    #    projects = paginator.page(page)
    #except PageNotAnInteger:
    #    projects = paginator.page(1)
    #except EmptyPage:
    #    projects = paginator.page(paginator.num_pages)
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
    return _projects(request, my_projects)


@login_required
def view_one_project(request, slug):
    """
    Public method that takes a request and a projecttitle, retrieves the Project object from the model
    with given projecttitle.  Renders projects/view_project.html
    # TODO: fix up return calls
    """
    project = get_object_or_404(Project, slug=slug)

    updates = project.get_updates()

    return render(request, 'projects/view_project.html', {
        'project': project , 'updates' :updates
        })

@login_required
def create_project(request):
    """
    Public method that creates a form and renders the request to create_project.html
    """

    enroll = Enrollment.objects.filter(user=request.user)
    cur_courses = Course.objects.filter(enrollment__in=enroll)
    no_postable_classes = False
    #If user is in 0 courses
    if len(enroll) == 0:
            #Redirect them to homepage and tell them to join a course
            messages.info(request,'You need to join a course before creating projects!')
            return HttpResponseRedirect('/')

    if len(cur_courses) == len(cur_courses.filter(limit_creation=True)):
        no_postable_classes = True

    if len(enroll) >= 1 and no_postable_classes:
            #Redirect them to homepage and tell them to join a course
            messages.info(request,'Professor has disabled Project Creation!')
            return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = ProjectForm(request.user.id, request.POST)
        if form.is_valid():
            # create an object for the input
            project = Project()
            project.title = form.cleaned_data.get('title')
            project.creator = request.user.username
            project.avail_mem = form.cleaned_data.get('accepting')
            project.sponsor = form.cleaned_data.get('sponsor')

            # Project content
            project.content = form.cleaned_data.get('content')

            # Project slug
            project.slug = form.cleaned_data.get('slug')

            # Local list of memebers, used to create Membership objects
            members = form.cleaned_data.get('members')

            project.save()
            # loop through the members in the object and make m2m rows for them
            for i in members:
                Membership.objects.create(user=i, project=project, invite_reason='')
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

    project = get_object_or_404(Project, slug=slug)

    #if user is not project owner
    if not request.user.username == project.creator:
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
                Membership.objects.create(user=i, project=project, invite_reason='')

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
