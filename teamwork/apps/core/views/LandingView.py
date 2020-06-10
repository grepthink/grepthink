"""Render 'Landing View' Page."""
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from teamwork.apps.courses.models import (Course, get_user_active_courses,
                                          get_user_disabled_courses)


def index(request):
    """The main index of grepthink, referred to as "Home" in the sidebar. Accessible to public and
    logged in users.

    TODO: get feed of project updates (or public projects) to display on login
    Args:
        request (requests.request): Page request.

    Returns:
        django.shortcuts.render: Page render.
    """
    # Render landing page for not logged in user
    logged_in = request.user.is_authenticated()
    if not logged_in:
        return render_landing(request)

    # If the user is a professor, render their dashboard
    if request.user.profile.isProf:
        return render_dashboard(request)

    # Otherwise render timeline
    return render_timeline(request)

def render_landing(request):
    """Render Landing Page.

    Args:
        request (requests.request): Page request.

    Returns:
        django.shortcuts.render: Page render.
    """
    page_name = "Grepthink"
    page_description = "Build Better Teams"
    title = "Welcome"

    return render(request, 'core/landing.html', {
                'page_name' : page_name,
                'page_description' : page_description, 'title' : title
                })

def render_dashboard(request):
    """Render Professor Dashboard.

    Args:
        request (requests.request): Page request.

    Returns:
        django.shortcuts.render: Page render.
    """
    page_name = "Dashboard"
    page_description = "Instructor Control Panel"
    title = "Dashboard"
    active_courses = get_user_active_courses(request.user)
    disabled_courses = get_user_disabled_courses(request.user)

    return render(request, 'core/dashboard.html', {
        'page_name' : page_name,
        'page_description' : page_description, 'title' : title,
        'active_courses' : active_courses, 'disabled_courses': disabled_courses
        })

def render_timeline(request):
    """Render student timeline.

    Args:
        request (requests.request): Page request.

    Returns:
        django.shortcuts.render: Page render.
    """
    page_name = "Timeline"
    page_description = "Recent Updates from Courses and Projects"
    title = "Timeline"

    all_courses = get_user_active_courses(request.user)

    date_updates = []
    for course in all_courses:        
        date_updates.extend(course.get_updates_by_date())

    return render(request, 'core/index.html', {
        'page_name' : page_name,
        'page_description' : page_description, 'title' : title,
        'date_updates' : date_updates, 'logged_in' : True
        })

def disable(request, slug):
    """[summary]

    Args:
        request (requests.request): Page request.
        slug (str): A short label for something, containing only letters, numbers, underscores or hyphens.

    Returns:
        django.shortcuts.redirect: A page redirect.
    """
    course = get_object_or_404(Course, slug=slug)
    if request.user == course.creator or request.user.profile.isGT:
        course.disable = not course.disable
        course.save()

    return redirect('/')
