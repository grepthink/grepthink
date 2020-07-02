from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, redirect, render
from teamwork.apps.core.helpers import send_email
from teamwork.apps.courses.forms import (AssignmentForm, CourseUpdateForm,
                                         EditAssignmentForm)
from teamwork.apps.courses.models import (Assignment, Course, CourseUpdate,
                                          Enrollment)
from teamwork.apps.profiles.models import Profile
from teamwork.apps.projects.models import Interest, Membership, Project


@login_required
def view_one_course(request, slug):
    """
    Public method that takes a request and a coursename, retrieves the Course object from the model
    with given coursename.

    Renders courses/view_course.html
    """
    course = get_object_or_404(Course.objects.prefetch_related('creator', 'students', 'projects'), slug=slug)
    page_name = "%s"%(course.name)
    page_description = "Course Overview"
    title = "%s"%(slug)

    # Get the user_role
    if not request.user.profile.isGT:
        # check if current user is enrolled in the course
        if request.user in course.students.all() or (request.user == course.creator):
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
    staff_ids = [o.id for o in staff]
    students = list(course.students.exclude(id__in=staff_ids))
    asgs = sorted(course.assignments.all(), key=lambda s: s.ass_date)

    # Prepare a list of students not in a project for count and color coding
    available = []
    taken_ids = list(Membership.objects.prefetch_related('user').values_list('user', flat=True).filter(project__in=course.projects.all()))
    available = list(course.students.exclude(id__in=taken_ids+staff_ids))

    assignment_form = AssignmentForm(request.user.id, slug)
    if request.method == 'POST':
        # TODO: only allow professors to create? why initialize assignment_form again?
        assignment_form = AssignmentForm(request.user.id, slug, request.POST)
        if assignment_form.is_valid():
            assignment = Assignment()
            assignment.due_date = assignment_form.cleaned_data.get('due_date')
            assignment.ass_date = assignment_form.cleaned_data.get('ass_date')
            assignment.ass_type =assignment_form.cleaned_data.get('ass_type').lower()
            assignment.ass_name = assignment_form.cleaned_data.get('ass_name')
            assignment.description = assignment_form.cleaned_data.get('description')
            assignment.ass_number = assignment_form.cleaned_data.get('ass_number')

            assignment.save()

            course.assignments.add(assignment)
            course.save()

        messages.info(request, 'You have successfully created an assignment')
        return redirect(view_one_course, course.slug)

    return render(
        request, 'courses/view_course.html',
        {'assignmentForm':assignment_form,
         'course': course, 'projects': projects, 'date_updates': date_updates, 'students':students,
         'user_role': user_role, 'available':available, 'assignments':asgs, 'has_shown_interest':has_shown_interest,
         'page_name': page_name, 'page_description': page_description, 'title': title, 'prof': prof, 'tas': tas})

@login_required
def edit_assignment(request, slug):
    """Edit assignment method, creating generic form."""
    assignment = get_object_or_404(Assignment.objects.prefetch_related('course'), slug=slug)
    course = assignment.course.first()
    page_name = "Edit Assignment"
    page_description = "Edit %s"%(assignment.ass_name)
    title = "Edit Assignment"

    if not request.user.profile.isGT:
        enrollment = Enrollment.objects.filter(user=request.user, course=course)
        if enrollment.exists():
            user_role = enrollment.first().role
        else:
            # User isn't enrolled in the course
            messages.info(request, 'You must be enrolled in the course to Edit Assignments')

            # Using HttpResponseRedirect due to cyclical imports if we import view_courses
            return HttpResponseRedirect('/course/')
    else:
        user_role = 'GT'

    if request.user.profile.isGT:
        pass
    #if user is not a professor or they did not create course
    elif not course.creator == request.user:
        if user_role != "ta":
            #redirect them to the /course directory with message
            messages.info(request, 'Only a Professor or TA can Edit an Assignment')

            # Using HttpResponseRedirect due to cyclical imports if we import view_courses
            return HttpResponseRedirect('/course/')

    if request.method == 'POST':
        assignment_form = EditAssignmentForm(request.user.id, slug, request.POST)
        if assignment_form.is_valid():
            data = assignment_form.cleaned_data
            due_date = data.get('due_date')
            ass_date = data.get('ass_date')
            ass_type = data.get('ass_type').lower()
            ass_name = data.get('ass_name')
            description = data.get('description')
            ass_number = data.get('ass_number')

            # edit the current assignment's properties w/ the new values
            assignment.due_date = due_date
            assignment.ass_date = ass_date
            assignment.ass_type = ass_type
            assignment.ass_name = ass_name
            assignment.description = description
            assignment.ass_number = ass_number
            assignment.save()

        return redirect(view_one_course, course.slug)

    form = EditAssignmentForm(request.user.id, slug, instance=assignment)

    return render(
        request, 'courses/edit_assignment.html',
        {'assignmentForm': form, 'course': course, 'ass':assignment,
         'page_name' : page_name, 'page_description': page_description, 'title': title}
        )

@login_required
def delete_assignment(request, slug):
    """Delete assignment method."""
    assignment = get_object_or_404(Assignment, slug=slug)
    course = assignment.course.first()

    if not request.user.profile.isGT:
        user_role = Enrollment.objects.filter(user=request.user, course=course).first().role
    else:
        user_role = 'GT'

    if request.user.profile.isGT:
        pass
    # If request.user is NOT the course creator and NOT a TA, then redirect them
    elif not request.user == course.creator:
        if user_role != "ta":
            return redirect(view_one_course, course.slug)

    # Runs through each assignment submission and deletes them
    for submission in assignment.subs.all():
        submission.delete()

    #deletes the assignment
    assignment.delete()

    # Redirect to view_one_course
    return redirect(view_one_course, course.slug)

@login_required
def update_course(request, slug):
    """Post an update for a given course."""
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
        messages.info(request, 'Only Professor can post a course update')
        return HttpResponseRedirect('/course')

    if request.method == 'POST':
        form = CourseUpdateForm(request.user.id, request.POST)
        if form.is_valid():
            new_update = CourseUpdate(course=course)
            new_update.course = course
            new_update.title = form.cleaned_data.get('title')
            new_update.content = form.cleaned_data.get('content')
            new_update.creator = request.user
            new_update.save()

            # grab list of students in the course
            students_in_course = course.students.all().filter()

            # Send Email notification to Students in Course
            subject = "{0} has posted an update to {1}".format(request.user, course.name)
            content = "{0}\n\n www.grepthink.com".format(new_update.content)
            send_email(students_in_course, "noreply@grepthink.com", subject, content)

            # Notify the User of success
            messages.add_message(request, messages.SUCCESS, "Posted and Email Sent!")

            return redirect(view_one_course, course.slug)
    else:
        form = CourseUpdateForm(request.user.id)

    return render(
        request, 'courses/update_course.html',
        {'form': form, 'course': course, 'page_name' : page_name, 'page_description': page_description, 'title': title }
        )

@login_required
def update_course_update(request, slug, course_update_id):
    """Edit an update for a given course."""
    course = get_object_or_404(Course, slug=slug)
    update = get_object_or_404(CourseUpdate, id=course_update_id)

    if request.user.profile.isGT:
        pass
    elif update.creator != request.user:
        return redirect(view_one_course, course.slug)

    if request.method == 'POST':
        form = CourseUpdateForm(request.user.id, request.POST)
        if form.is_valid():
            update.course = course
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
def delete_course_update(request, slug, course_update_id):
    """Delete an update for a given course."""
    course = get_object_or_404(Course, slug=slug)
    update = get_object_or_404(CourseUpdate, id=course_update_id)

    if update.creator == request.user or request.user.profile.isGT:
        update.delete()

    return redirect(view_one_course, course.slug)

@login_required
def claim_projects(request, slug):
    """ View to Claim Projects to be TA for """
    page_name = "Claim Projects"
    page_description = "Select the projects that you are assigned to"
    title = "Claim Projects"

    course = get_object_or_404(Course.objects.prefetch_related('projects'), slug=slug)
    projects = course.projects.all()
    profile = Profile.objects.prefetch_related('claimed_projects').get(user=request.user)
    claimed_projects = profile.claimed_projects.all()
    available = get_available_projects(request.user, course)

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
            # todo: this needs to be reworked
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

def get_available_projects(user, course):
    """ Gets all unclaimed projects in a course that are still available for a TA to claim """

    profile = Profile.objects.prefetch_related('claimed_projects').get(user=user)

    # Grab list of already claimed projects by the current user/profile
    filtered = profile.claimed_projects.filter(course=course)

    # todo: this needs to be reworked
    # Build List of Projects that are available to be claimed
    available = []
    for proj in course.projects.all():
        found = False
        for p in filtered:
            if proj == p:
                found = True
        if not found:
            available.append(proj)

    return available
