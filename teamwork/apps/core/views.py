"""
Core views provide main site functionality.

"""
from .models import *
from .forms import *

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from teamwork.apps.courses.models import *
from teamwork.apps.projects.models import *

def login_view(request):
    if request.user.is_authenticated():
        # TODO: get feed of project updates (or public projects) to display on login
        return render(request, 'courses/view_course.html')
    else:
        # Redirect user to login instead of public index (for ease of use)
        return render(request, 'core/login.html')

def index(request):
    """
    The main index of Teamwork, referred to as "Home" in the sidebar.
    Accessible to public and logged in users.
    """
    # TODO: get feed of project updates (or public projects) to display on login

    # Populate with defaults for not logged in user
    page_name = "Explore"
    page_description = "Public Projects and Courses"
    date_updates = None

    if request.user.is_authenticated():
        page_name = "Timeline"
        page_description = "Recent Updates from Courses and Projects"
        all_courses = Course.get_my_courses(request.user)
        date_updates = []
        for course in all_courses:
            date_updates.extend(course.get_updates_by_date())

    return render(request, 'core/index.html', {'page_name' : page_name,
         'page_description' : page_description, 'date_updates' : date_updates})

def about(request):
    return render(request, 'core/about.html')

@login_required
def view_matches(request):
    """
    Generic view for serving a list of projects and potential teammate matches for
        each project.
    """
    project_match_list = []
    course_set = []

    if request.user.profile.isProf:
        # print("Begin Best Matches")
        courses = Course.get_my_created_courses(request.user)
        # print(courses)
        for course in courses:
            for project in course.projects.all():
                p_match = po_match(project)
                project_match_list.extend([(course, project, p_match)])
            course_set.append(course)
        # print(course_set)
        # print(project_match_list)
    else:
        projects = Project.get_my_projects(request.user)

        # print("PROJECTS:")
        # print(projects)

        for project in projects:
            # print("Project:")
            # print(project)
            p_match = po_match(project)
            # print("p_match:")
            # print(p_match)
            project_match_list.extend([(project, p_match)])

        # print("Project Match List:")
        # print(project_match_list)

        # for project in project_match_list:
            # print("project in project_match_list")
            # print(project)
            # print(project[0].title)
            # if project[1]:
            #     print(project[1][0].username)

    return render(request, 'core/view_matches.html', {
        'project_match_list' : project_match_list, 'course_set': course_set
        })
