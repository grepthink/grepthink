# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.urlresolvers import reverse

import json

# Imported Methods/Classes
from teamwork.apps.core.models import *
from teamwork.apps.projects.models import ResourceUpdate, Project
from teamwork.apps.profiles.models import Alert
from teamwork.apps.projects.forms import UpdateForm, ResourceForm

from teamwork.apps.projects.views.BaseView import get_user_role
from teamwork.apps.projects.views.MyProjectsView import *
from teamwork.apps.courses.views.CourseView import view_one_course

from teamwork.apps.projects.forms import *
from teamwork.apps.core.helpers import *

@login_required
def view_one_project(request, slug):
    """
    Public method that takes a request and a slug, retrieves the Project object
    from the model with given project slug.  Renders projects/view_project.html

    Passing status check unit test in test_views.py.
    """

    project=get_object_or_404(Project.objects.select_related('scrum_master', 'creator', 'ta').prefetch_related('creator__profile',
                                                                                                              'members',
                                                                                                              'members__profile',
                                                                                                              'desired_skills',
                                                                                                              'course',
                                                                                                              'course__assignments',
                                                                                                              'pending_members',
                                                                                                              'tsr'),
                                                                                                              slug=slug)
    # Populate with project name and tagline
    page_name = project.title or "Project"
    page_description = project.tagline or "Tagline"
    title = project.title or "Project"

    # Local Variables
    updates = project.get_updates()
    resources = project.get_resources()
    course = project.course.first()
    staff = course.get_staff()
    asgs = sorted(course.assignments.prefetch_related('subs').all(), key=lambda s: s.ass_date)
    asg_completed = []

    for i in asgs:
        for j in i.subs.prefetch_related('evaluator').all():
            if j.evaluator == request.user:
                asg_completed.append(i)
                break

    pending_members = project.pending_members.all()
    pending_count = len(pending_members)

    # If the current user is on the Pending List, requestButton bool hides the RequestToJoin button
    requestButton = 1
    if request.user in pending_members:
        requestButton = 0

    readable = ""
    if project.readable_meetings:
        jsonDec = json.decoder.JSONDecoder()
        readable = jsonDec.decode(project.readable_meetings)

    completed_tsrs = project.tsr.all().prefetch_related('evaluator', 'evaluatee')
    avg_dict = {}
    for i in completed_tsrs.all():
        if i.evaluatee in avg_dict.keys():
            avg_dict[i.evaluatee] = int(avg_dict[i.evaluatee]) + int(i.percent_contribution)
        else:
            avg_dict[i.evaluatee] = int(i.percent_contribution)

    avgs = []
    for key, item in avg_dict.items():
        try:
            con_avg = item / (len(completed_tsrs) / len(project.members.all()))
        except:
            con_avg = -1    # if dividing by zero set avg to -1
        avgs.append((key, int(con_avg)))

    assigned_tsrs = sorted(course.assignments.filter(ass_type="tsr", closed=False), key=lambda s: s.ass_date)
    tsr_tuple={}

    user_role = get_user_role(request.user, course)
    fix = []
    if request.user.profile.isGT or request.user.profile.isProf or user_role=="ta":
        fix = sorted(project.tsr.all().prefetch_related('evaluator', 'evaluatee', 'ass'), key=lambda x: (x.ass_number, x.evaluatee.username))
        # temp = ""
        #
        # for j in temp_tup:
        #     if temp != j.evaluatee:
        #         temp = j.evaluatee
        #         fix.append([temp, j.ass.first(), j, 1])
        #     else:
        #         fix.append(["", j.ass.first(), j, 0])
    else:
        fix = None

    med = 100

    if len(project.members.all()) > 0:
        med = int(100/len(project.members.all()))

    mid = {'low' : int(med*0.7), 'high' : int(med*1.4)}
    # ======================
    today = datetime.datetime.now().date()

    return render(request, 'projects/view_project.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title, 'temp_tup':fix,
        'pending_members': pending_members,
        'requestButton':requestButton, 'avgs':avgs, 'assignments':asgs, 'asg_completed':asg_completed,'today':today,
        'pending_count':pending_count,'staff':staff,
        'updates': updates, 'course' : course,
        'meetings': readable, 'resources': resources, 'json_events': project.meetings, 'contribute_levels' : mid, 'assigned_tsrs': assigned_tsrs,
        'project': project})

@login_required
def request_join_project(request, slug):
    project = get_object_or_404(Project.objects.select_related('creator').prefetch_related('members', 'pending_members', 'course'), slug=slug)
    project_members = project.members.all()
    pending_members = project.pending_members.all()

    user_role = get_user_role(request.user, project.course.first())
    # If the user is enrolled in the course, then allow them to request to join
    if user_role != 'not enrolled':
        if request.user in project_members:
            # TODO: send an error
            print("need this print here until we put something in")
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

def reject_member(request, slug, uname):
    """
    Reject Membership
    """
    project = get_object_or_404(Project.objects.prefetch_related('pending_members'), slug=slug)
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
def post_update(request, slug):
    """
    Post an update for a given project
    """
    project = get_object_or_404(Project.objects.select_related('creator').prefetch_related('members'), slug=slug)
    course = project.course.first()

    page_name = "Project Update"
    page_description = project.title

    if request.user.profile.isGT or request.user in course.get_staff():
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
            messages.add_message(request, messages.SUCCESS, "Project update posted!")
            return redirect(view_one_project, project.slug)
    else:
        form = UpdateForm(request.user.id)
    return render(request, 'projects/post_update.html',
                  {'form': form, 'page_name': page_name, 'page_description': page_description,
                   'project': project, 'course': course})

@login_required
def update_project_update(request, slug, id):
    """
    Edit an update for a given project
    """
    project = get_object_or_404(Project, slug=slug)
    update = get_object_or_404(ProjectUpdate, id=id)
    course = project.course.first()

    page_name = "Project Update"
    page_description = project.title

    if request.user.profile.isGT:
        pass
    elif update.user != request.user:
        return redirect(view_one_project, project.slug)

    if request.method == 'POST':
        form = UpdateForm(request.user.id, request.POST)
        if form.is_valid():
            update.project = project
            update.update_title = form.cleaned_data.get('update_title')
            update.update = form.cleaned_data.get('update')
            if not request.user.profile.isGT:
                update.user = request.user
            update.save()
            messages.add_message(request, messages.SUCCESS, "Project update edited")
            return redirect(view_one_project, project.slug)
    else:
        form = UpdateForm(request.user.id, instance=update)

    return render(
            request, 'projects/update_post_update.html',
            {'form': form, 'page_name': page_name, 'page_description': page_description, 'project': project, 'course': course, 'update': update}
            )

@login_required
def delete_project_update(request, slug, id):
    """
    Delete an update for a given project
    """
    project = get_object_or_404(Project, slug=slug)
    update = get_object_or_404(ProjectUpdate, id=id)

    if update.user == request.user or request.user.profile.isGT:
        messages.add_message(request, messages.ERROR, "Project update deleted")
        update.delete()

    return redirect(view_one_project, project.slug)

@login_required
def resource_update(request, slug):
    """
    Post a Resource to the project given the slug
    """
    project = get_object_or_404(Project.objects.select_related('creator').prefetch_related('members'), slug=slug)
    course = project.course.first()

    page_name = "Add Resource"
    page_description = project.title

    if request.user.profile.isGT or request.user in course.get_staff():
        pass
    elif not request.user == project.creator and request.user not in project.members.all(
    ):
        #redirect them with a message
        messages.info(request, 'Only current members can post a resource for a project!')
        return HttpResponseRedirect('/project/all')

    if request.method == 'POST':
        form = ResourceForm(request.user.id, request.POST)
        if form.is_valid():
            new_update = ResourceUpdate(project=project)
            new_update.src_link = form.cleaned_data.get('src_link')
            new_update.src_title = form.cleaned_data.get('src_title')
            new_update.user = request.user
            new_update.save()
            messages.add_message(request, messages.SUCCESS, "Project resource added")
            return redirect(view_one_project, project.slug)
    else:
        form = ResourceForm(request.user.id)

    return render(request, 'projects/add_resource.html',
                {'form': form, 'page_name': page_name, 'page_description': page_description, 'course': course, 'project': project})

@login_required
def update_resource_update(request, slug, id):
    """
    Edit a resource for a given project
    """
    project = get_object_or_404(Project, slug=slug)
    resource = get_object_or_404(ResourceUpdate, id=id)
    course = project.course.first()

    page_name = "Edit Resource "
    page_description = project.title

    if request.user.profile.isGT:
        pass
    elif resource.user != request.user:
        return redirect(view_one_project, project.slug)

    if request.method == 'POST':
        form = ResourceForm(request.user.id, request.POST)
        if form.is_valid():
            resource.src_link = form.cleaned_data.get('src_link')
            resource.src_title = form.cleaned_data.get('src_title')
            if not request.user.profile.isGT:
                resource.user = request.user
            resource.save()
            messages.add_message(request, messages.SUCCESS, "Project resource edited")
            return redirect(view_one_project, project.slug)
    else:
        form = ResourceForm(request.user.id, instance=resource)

    return render(
            request, 'projects/update_resource_update.html',
            {'form': form, 'page_name': page_name, 'page_description': page_description, 'project': project, 'course': course, 'resource': resource}
            )

@login_required
def delete_resource_update(request, slug, id):
    """
    Delete an resource for a given project
    """
    project = get_object_or_404(Project, slug=slug)
    resource = get_object_or_404(ResourceUpdate, id=id)

    if resource.user == request.user or request.user.profile.isGT:
        messages.add_message(request, messages.ERROR, "Project resource deleted")
        resource.delete()

    return redirect(view_one_project, project.slug)
