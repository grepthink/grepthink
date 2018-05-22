from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from teamwork.apps.courses.models import Course

def index(request):
    """
    The main index of Teamwork, referred to as "Home" in the sidebar.
    Accessible to public and logged in users.
    """
    # TODO: get feed of project updates (or public projects) to display on login

    # Populate with defaults for not logged in user
    page_name = "Grepthink"
    page_description = "Build Better Teams"
    title = "Welcome"
    date_updates = None
    logged_in = request.user.is_authenticated();

    if not logged_in:
        return render(request, 'core/landing.html', {'page_name' : page_name,
            'page_description' : page_description, 'title' : title})

    # If the user is a professor, return the dashboard html
    if logged_in and request.user.profile.isProf:
        page_name = "Dashboard"
        page_description = "Instructor Control Panel"
        title = "Dashboard"
        all_courses = Course.get_my_created_courses(request.user)
        return render(request, 'core/dashboard.html', {'page_name' : page_name,
         'page_description' : page_description, 'title' : title,
         'all_courses' : all_courses})

    if logged_in:
        page_name = "Timeline"
        page_description = "Recent Updates from Courses and Projects"
        title = "Timeline"
        if (request.user.profile.isProf):
            all_courses = Course.get_my_created_courses(request.user)
        else:
            all_courses = Course.get_my_courses(request.user)
        date_updates = []
        for course in all_courses:
            course_updates = course.get_updates_by_date()
            date_updates.extend(course.get_updates_by_date())

    return render(request, 'core/index.html', {'page_name' : page_name,
         'page_description' : page_description, 'title' : title,
         'date_updates' : date_updates, 'logged_in' : logged_in})
