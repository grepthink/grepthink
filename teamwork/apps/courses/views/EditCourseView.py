from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from teamwork.apps.courses.models import Course, Enrollment
from teamwork.apps.courses.views.CourseView import view_one_course
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse

from teamwork.apps.profiles.models import Alert
from teamwork.apps.courses.forms import EditCourseForm

@login_required
def edit_course(request, slug):
    """
    Edit course method, creating generic form
    https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-editing/
    """
    course = get_object_or_404(Course.objects.prefetch_related('creator'), slug=slug)
    page_name = "Edit Course"
    page_description = "Edit %s"%(course.name)
    title = "Edit Course"

    enrollments = Enrollment.objects.filter(user=request.user, course=course)
    tas = Enrollment.objects.filter(course=course, role="ta")
    students = Enrollment.objects.filter(course=course, role="student")

    if request.user.profile.isGT:
        userRole = 'GT'
    else:
        if enrollments.count():
            userRole = enrollments.first().role
        else:
            userRole = "not enrolled"

    if request.user.profile.isGT:
        pass
    #if user is not a professor or they did not create course
    elif not course.creator == request.user:
        # if user is not a TA
        if not userRole=="ta":
            #redirect them to the /course directory with message
            messages.info(request,'Only Professor can edit course')
            return HttpResponseRedirect('/course')

    # Add a member to the course
    if request.POST.get('members'):
        # Get the members to add, as a list
        members = request.POST.getlist('members')
        enrollments = Enrollment.objects.filter(course=course)
        students = course.students.all()
        added = False

        # Create membership objects for the newly added members
        for uname in members:
            mem_to_add = User.objects.get(username=uname)
            mem_courses = Course.get_my_courses(mem_to_add)

            # Don't add a member if they already have membership in course
            # Confirm that the member is a part of the course
            # List comprehenshion: loops through this courses memberships in order
            #   to check if mem_to_add is in the user field of a current membership.
            if not course in mem_courses:
                if not mem_to_add in students:
                    Enrollment.objects.create(user=mem_to_add, course=course, role="student")
                    Alert.objects.create(
                        sender=request.user,
                        to=mem_to_add,
                        msg="You were added to: " + course.name,
                        url=reverse('view_one_course',args=[course.slug]),
                        )
                    added = True
        if added:
            messages.add_message(request, messages.SUCCESS, "Successfully added member(s) to course.")
        else:
            messages.add_message(request, messages.SUCCESS, "Student(s) already added to course.")

        # return redirect(edit_course, slug)

    # Remove a user from the course
    if request.POST.get('remove_user'):
        members = request.POST.getlist('remove_user')
        removed = False

        for mem in members:
            f_user = User.objects.get(username=mem)
            to_delete = Enrollment.objects.filter(user=f_user, course=course, role="student")

            for mem_obj in to_delete:
                Alert.objects.create(
                    sender=request.user,
                    to=f_user,
                    msg="You were removed from: " + course.name,
                    url=reverse('view_one_course',args=[course.slug]),
                    )
                mem_obj.delete()
                removed = True
        if removed:
            messages.add_message(request, messages.SUCCESS, "Member(s) successfully removed from the course.")
        else:
            messages.add_message(request, messages.SUCCESS, "Failed to succesfully remove member(s) from the course.")

        # return redirect(edit_course, slug)

    # Add a TA
    if request.POST.get('ta'):
        # Get the members to add, as a list
        members = request.POST.getlist('ta')
        enrollments = Enrollment.objects.filter(course=course)
        students = course.students.all()

        # Create membership objects for the newly added members
        for uname in members:
            mem_to_add = User.objects.get(username=uname)
            mem_courses = Course.get_my_courses(mem_to_add)

            # Don't add a member if they already have membership in course
            # Confirm that the member is a part of the course
            # List comprehenshion: loops through this courses memberships in order
            #   to check if mem_to_add is in the user field of a current membership.
            if mem_to_add in students:
                Enrollment.objects.filter(user=mem_to_add).update(role="ta")
            else:
                Enrollment.objects.create(user=mem_to_add, course=course, role="ta")
                Alert.objects.create(
                    sender=request.user,
                    to=mem_to_add,
                    msg="You were added to: " + course.name + " as a TA",
                    url=reverse('view_one_course',args=[course.slug]),
                    )

        messages.add_message(request, messages.SUCCESS, "Successfully added TA to the course.")

        # return redirect(edit_course, slug)

    # Remove a ta from the course
    if request.POST.get('remove_ta'):
        f_username = request.POST.get('remove_ta')
        f_user = User.objects.get(username=f_username)
        to_delete = Enrollment.objects.filter(user=f_user, course=course, role="ta")

        for mem_obj in to_delete:
            Alert.objects.create(
                sender=request.user,
                to=f_user,
                msg="You were removed as the TA from: " + course.name,
                url=reverse('view_one_course',args=[course.slug]),
                )
            mem_obj.delete()

        messages.add_message(request, messages.SUCCESS, "Removed TA from Course.")

        # return redirect(edit_course, slug)

    if request.method == 'POST':
        # send the current user.id to filter out
        form = EditCourseForm(request.user.id, slug, request.POST, request.FILES)
        if form.is_valid():
            # edit the course object, omitting slug
            data = form.cleaned_data
            course.name = data.get('name')
            course.info = data.get('info')
            course.term = data.get('term')
            course.limit_creation = data.get('limit_creation')
            course.limit_weights = data.get('limit_weights')
            course.weigh_interest = data.get('weigh_interest') or 0
            course.weigh_know = data.get('weigh_know') or 0
            course.weigh_learn = data.get('weigh_learn') or 0
            course.limit_interest = data.get('limit_interest')
            course.save()
        else:
            print("FORM ERRORS: ", form.errors)

        return redirect(view_one_course, course.slug)
    else:
        form = EditCourseForm(request.user.id, slug,  instance=course)

    return render(
            request, 'courses/edit_course.html',
            {'form': form,'course': course, 'tas':tas, 'students':students, 'page_name' : page_name, 'page_description': page_description, 'title': title}
            )

@login_required
def delete_course(request, slug):
    """
    Delete course method
    TODO: delete should be moved to Course model ie: Course.DeleteGraph()
    """
    course = get_object_or_404(Course, slug=slug)
    projects = course.projects.all()
    assignments = course.assignments.all()
    course_updates = course.get_updates()
    course_alerts = Alert.objects.filter(url__contains=course.slug).filter(msg__contains=course.name)

    if request.user.profile.isGT:
        pass
    elif not request.user==course.creator:
        messages.add_message(request, messages.ERROR, "Only Professors can delete a course. Shame on you")
        return redirect(view_one_course, course.slug)

    # Runs through each project and deletes them
    for p in projects:
        for t in p.tsr.all():
            t.delete()
        for i in p.interest.all():
            i.delete()
        project_alerts = Alert.objects.filter(url__contains=p.slug).filter(msg__contains=p.title)
        for pa in project_alerts:
            pa.delete()
        p.delete()

    for a in assignments:
        a.delete()

    for c in course_updates:
        c.delete()

    for ca in course_alerts:
        ca.delete()

    #deletes course
    course.delete()
    return HttpResponseRedirect('/course/')



def lock_interest(request, slug):
    """
    Lock the interest for a course
    """
    course = get_object_or_404(Course, slug=slug)
    if course.limit_interest:
        course.limit_interest = False
    else:
        course.limit_interest = True

    course.save()
    return redirect(view_one_course, course.slug)

def disable(request, slug):
    """
    Lock the interest for a course
    """
    course = get_object_or_404(Course, slug=slug)
    if request.user == course.creator or request.user.profile.isGT:
        if course.disable:
            course.disable = False
            course.save()
            messages.add_message(request, messages.SUCCESS, course.name +  " has been re-enabled")
            return redirect(view_one_course, course.slug)
        else:
            course.disable = True
            course.save()
            messages.add_message(request, messages.SUCCESS, course.name +  " has been disabled")
            return redirect('/course')
