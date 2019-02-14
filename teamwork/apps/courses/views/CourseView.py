from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)

from teamwork.apps.courses.models import Course, Enrollment, Assignment, CourseUpdate
from teamwork.apps.projects.models import Membership, Project, Interest
from teamwork.apps.profiles.models import Profile
from teamwork.apps.courses.forms import AssignmentForm, EditAssignmentForm, CourseUpdateForm
from teamwork.apps.core.helpers import send_email

@login_required
def view_one_course(request, slug):
    """
    Public method that takes a request and a coursename, retrieves the Course object from the model
    with given coursename.  Renders courses/view_course.html
    """
    course = get_object_or_404(Course.objects.prefetch_related('creator', 'students', 'projects'), slug=slug)
    page_name = "%s"%(course.name)
    page_description = "Course Overview"
    title = "%s"%(slug)

    # Get the user_role
    if not request.user.profile.isGT:
        # check if current user is enrolled in the course
        if request.user in course.students.all() or (request.user==course.creator):
            try:
                user_role = Enrollment.objects.filter(user=request.user, course=course).first().role
            except:
                user_role = "not enrolled"
        else:
            # init user_role otherwise
            user_role = "not enrolled"
    else:
        user_role = 'GT'

    # Misc list needed
    temp_projects = course.projects.all()
    # sort the list of projects alphabetical, but not case sensitive (aka by ASCII)
    projects = sorted(temp_projects, key=lambda s: s.title.lower())
    date_updates = course.get_updates_by_date()

    # all_interests = Interest.objects.filter(project_interest=temp_projects,user=request.user)

    has_shown_interest = False
    for project in temp_projects:
        user_interests = Interest.objects.filter(project_interest=project, user=request.user)

        if user_interests:
            has_shown_interest = True
            break

    staff = course.get_staff()
    tas = course.get_tas()
    prof = course.creator

    # Grab Students in the course
    staff_ids=[o.id for o in staff]
    students =list(course.students.exclude(id__in=staff_ids))
    asgs = sorted(course.assignments.all(), key=lambda s: s.ass_date)

    # Prepare a list of students not in a project for count and color coding
    available=[]
    taken_ids=list(Membership.objects.prefetch_related('user').values_list('user', flat=True).filter(project__in=course.projects.all()))
    available=list(course.students.exclude(id__in=taken_ids+staff_ids))

    assignmentForm = AssignmentForm(request.user.id, slug)
    if(request.method == 'POST'):
        assignmentForm = AssignmentForm(request.user.id, slug, request.POST)
        if assignmentForm.is_valid():
            assignment = Assignment()
            assignment.due_date = assignmentForm.cleaned_data.get('due_date')
            assignment.ass_date = assignmentForm.cleaned_data.get('ass_date')
            assignment.ass_type =assignmentForm.cleaned_data.get('ass_type').lower()
            assignment.ass_name = assignmentForm.cleaned_data.get('ass_name')
            assignment.description = assignmentForm.cleaned_data.get('description')
            assignment.ass_number = assignmentForm.cleaned_data.get('ass_number')

            assignment.save()

            course.assignments.add(assignment)
            course.save()

        messages.info(request, 'You have successfully created an assignment')
        return redirect(view_one_course,course.slug)

    return render(request, 'courses/view_course.html', {'assignmentForm':assignmentForm,
        'course': course , 'projects': projects, 'date_updates': date_updates, 'students':students,
        'user_role':user_role, 'available':available, 'assignments':asgs, 'has_shown_interest':has_shown_interest,
        'page_name' : page_name, 'page_description': page_description, 'title': title, 'prof': prof, 'tas': tas})

@login_required
def edit_assignment(request, slug):
    """
    Edit assignment method, creating generic form
    """
    user = request.user
    ass = get_object_or_404(Assignment.objects.prefetch_related('course'), slug=slug)
    course = ass.course.first()
    page_name = "Edit Assignment"
    page_description = "Edit %s"%(ass.ass_name)
    title = "Edit Assignment"

    if not request.user.profile.isGT:
        user_role = Enrollment.objects.filter(user=request.user, course=course).first().role
    else:
        user_role = 'GT'

    if request.user.profile.isGT:
        pass
    #if user is not a professor or they did not create course
    elif not course.creator == request.user:
        if not user_role=="ta":
            #redirect them to the /course directory with message
            messages.info(request,'Only a Professor or TA can Edit an Assignment')
            return HttpResponseRedirect('/course')

    if(request.method == 'POST'):
        assignmentForm = EditAssignmentForm(request.user.id, slug, request.POST)
        if assignmentForm.is_valid():
            data = assignmentForm.cleaned_data
            due_date = data.get('due_date')
            ass_date = data.get('ass_date')
            ass_type = data.get('ass_type').lower()
            ass_name = data.get('ass_name')
            description = data.get('description')
            ass_number = data.get('ass_number')

            # edit the current assignment's properties w/ the new values
            ass.due_date = due_date
            ass.ass_date = ass_date
            ass.ass_type = ass_type
            ass.ass_name = ass_name
            ass.description = description
            ass.ass_number = ass_number
            ass.save()
        else:
            print("FORM ERRORS: ", assignmentForm.errors)

        return redirect(view_one_course,course.slug)

    else:
        form = EditAssignmentForm(request.user.id, slug, instance=ass)

    return render(
            request, 'courses/edit_assignment.html',
            {'assignmentForm': form,'course': course, 'ass':ass, 'page_name' : page_name, 'page_description': page_description, 'title': title}
            )

@login_required
def delete_assignment(request, slug):
    """
    Delete assignment method
    """
    ass = get_object_or_404(Assignment, slug=slug)
    course = ass.course.first()

    if not request.user.profile.isGT:
        user_role = Enrollment.objects.filter(user=request.user, course=course).first().role
    else:
        user_role = 'GT'

    print("user_role",user_role)

    if request.user.profile.isGT:
        pass
    elif not request.user==course.creator:
        if not user_role == "ta":
            return redirect(view_one_course, course.slug)

    #Runs through each project and deletes them
    for a in ass.subs.all():
        a.delete()

    #deletes course
    ass.delete()
    return redirect(view_one_course, course.slug)

@login_required
def update_course(request, slug):
    """
    Post an update for a given course
    """
    course = get_object_or_404(Course.objects.prefetch_related('creator'), slug=slug)
    page_name = "Update Course"
    page_description = "Update %s"%(course.name) or "Post a new update"
    title = "Update Course"

    if not request.user.profile.isGT:
        user_role = Enrollment.objects.filter(user=request.user, course=course).first().role
    else:
        user_role = 'GT'

    if user_role == "student":
        #redirect them to the /course directory with message
        messages.info(request,'Only Professor can post a course update')
        return HttpResponseRedirect('/course')

    if request.method == 'POST':
        form = CourseUpdateForm(request.user.id, request.POST)
        if form.is_valid():
            new_update = CourseUpdate(course=course)
            new_update.course = course;
            new_update.title = form.cleaned_data.get('title')
            new_update.content = form.cleaned_data.get('content')
            new_update.creator = request.user
            new_update.save()

        # Next 4 lines handle sending an email to class roster
            # grab list of students in the course
            students_in_course = course.students.all().filter()
            # TODO: course variables contains (slug: blah blah)
            subject = "{0} has posted an update to {1}".format(request.user, course)
            content = "{0}\n\n www.grepthink.com".format(new_update.content)
            send_email(students_in_course, "noreply@grepthink.com", subject, content)
            messages.add_message(request, messages.SUCCESS, "Posted and Email Sent!")

            return redirect(view_one_course, course.slug)
    else:
        form = CourseUpdateForm(request.user.id)

    return render(
            request, 'courses/update_course.html',
            {'form': form, 'course': course, 'page_name' : page_name, 'page_description': page_description, 'title': title }
            )

@login_required
def update_course_update(request, slug, id):
    """
    Edit an update for a given course
    """
    course = get_object_or_404(Course, slug=slug)
    update = get_object_or_404(CourseUpdate, id=id)

    if request.user.profile.isGT:
        pass
    elif update.creator != request.user:
        return redirect(view_one_course, course.slug)

    if request.method == 'POST':
        form = CourseUpdateForm(request.user.id, request.POST)
        if form.is_valid():
            update.course = course;
            update.title = form.cleaned_data.get('title')
            update.content = form.cleaned_data.get('content')
            if not request.user.profile.isGT:
                update.creator = request.user
            update.save()
            return redirect(view_one_course, course.slug)
    else:
        form = CourseUpdateForm(request.user.id, instance=update)

    return render(
            request, 'courses/update_course_update.html',
            {'form': form, 'course': course, 'update': update}
            )

@login_required
def delete_course_update(request, slug, id):
    """
    Delete an update for a given course
    """
    course = get_object_or_404(Course, slug=slug)
    update = get_object_or_404(CourseUpdate, id=id)

    if update.creator == request.user or request.user.prfile.isGT:
        update.delete()

    return redirect(view_one_course, course.slug)

@login_required
def claim_projects(request, slug):
    page_name = "Claim Projects"
    page_description = "Select the projects that you are assigned to"
    title = "Claim Projects"
    course = get_object_or_404(Course.objects.prefetch_related('projects'), slug=slug)
    user = request.user
    profile = Profile.objects.prefetch_related('claimed_projects').get(user=user)
    projects = course.projects.all()
    claimed_projects = profile.claimed_projects.all()
    filtered = profile.claimed_projects.filter(course=course)

    available = []
    for proj in projects:
        found = False
        for p in filtered:
            if (proj == p):
                found = True
        if not found:
            available.append(proj)

    if request.method == 'POST':

        if request.POST.get('remove_claim'):
            proj_name = request.POST.get('remove_claim')
            to_delete = get_object_or_404(Project, title=proj_name)
            to_delete.ta = course.creator
            to_delete.save()
            profile.claimed_projects.remove(to_delete)
            profile.save()
            messages.add_message(request, messages.SUCCESS, "Project's TA Fields updated.")

            return redirect(view_one_course, course.slug)

        if request.POST.get('select_projects'):
            to_claim = request.POST.getlist('select_projects')

            # manally search for project object with the same title
            to_claim_projects = []
            for proj in projects:
                for title in to_claim:
                    if proj.title == title:
                        to_add = get_object_or_404(Project, title=title)
                        to_claim_projects.append(to_add)

            for p in to_claim_projects:
                p.ta = request.user
                p.save()
                profile.claimed_projects.add(p)
                profile.save()
            messages.add_message(request, messages.SUCCESS, "Project's TA Fields updated.")
            return redirect(view_one_course, course.slug)

    return render(request, 'courses/claim_projects.html',
            {'course': course, 'available':available, 'claimed_projects':claimed_projects,
            'page_name' : page_name, 'page_description': page_description, 'title': title
            })
