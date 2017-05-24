"""
Core views provide main site functionality.

"""
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from teamwork.apps.courses.models import *
from teamwork.apps.projects.models import *

from .forms import *
from .models import *
import re


def login_view(request):
    page_name = "Login"
    page_description = ""
    title = "Login"
    if request.user.is_authenticated():
        # TODO: get feed of project updates (or public projects) to display on login
        return render(request, 'courses/view_course.html', {'page_name': page_name,
            'page_description': page_description, 'title' : title})
    else:
        # Redirect user to login instead of public index (for ease of use)
        return render(request, 'core/login.html', {'page_name': page_name,
            'page_description': page_description, 'title' : title})

def index(request):
    """
    The main index of Teamwork, referred to as "Home" in the sidebar.
    Accessible to public and logged in users.
    """
    # TODO: get feed of project updates (or public projects) to display on login

    # Populate with defaults for not logged in user
    page_name = "GrepThink"
    page_description = "Build Better Teams"
    title = "Welcome"
    date_updates = None
    logged_in = request.user.is_authenticated();

    if not logged_in:
        return render(request, 'core/landing.html', {'page_name' : page_name,
            'page_description' : page_description, 'title' : title})

    if logged_in:
        page_name = "Timeline"
        page_description = "Recent Updates from Courses and Projects"
        title = "Timeline"
        all_courses = Course.get_my_courses(request.user)
        date_updates = []
        for course in all_courses:
            date_updates.extend(course.get_updates_by_date())

    return render(request, 'core/index.html', {'page_name' : page_name,
         'page_description' : page_description, 'title' : title,
         'date_updates' : date_updates, 'logged_in' : logged_in})

def about(request):
    page_name = "About"
    page_description = "About"
    title = "About"
    return render(request, 'core/about.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title})

@login_required
def view_matches(request):
    """
    Generic view for serving a list of projects and potential teammate matches for
        each project.
    """
    project_match_list = []
    course_set = []

    page_name = "View Matches"
    page_description = "View Matching Students"
    title = "View Matches"

    if request.user.profile.isProf:
        courses = Course.get_my_created_courses(request.user)
        for course in courses:
            for project in course.projects.all():
                p_match = po_match(project)
                project_match_list.extend([(course, project, p_match)])
            course_set.append(course)
    else:
        my_projects = Project.get_my_projects(request.user)
        my_created = Project.get_created_projects(request.user)
        projects = my_projects | my_created
        projects = list(set(projects))
        for project in projects:
            p_match = po_match(project)
            project_match_list.extend([(project, p_match)])

    return render(request, 'core/view_matches.html', {
        'project_match_list' : project_match_list, 'course_set': course_set, 'page_name': page_name,
            'page_description': page_description, 'title' : title})


def auto_gen(request, slug):
    """
    Generic view for serving a list of projects and potential teammate matches for
        each project.
    """
    page_name = "Potential Roster"
    page_description = "Auto Generate Groups"
    title = "Auto Generate Groups"

    course = get_object_or_404(Course, slug=slug)
    project_match_list = []

    auto = auto_ros(course)

    # Get just the projects so partial_project_box.html can loop through easily.
    # Will have to changes this once we get a better ui for autogen.
    projects = [x[0] for x in auto]


    return render(request, 'core/auto_gen.html', {
        'auto_gen' : auto, 'course': course, 'projects':projects, 'page_name': page_name,
            'page_description': page_description, 'title' : title})

def matchstats(request, project_match_list, project):
    print("====================MATCHSTATS BITCHES =======================")
    """
        TODO:Logic around cur_project needs some changing, need to get all projects in a course
        i.e. get_all_projects instead of get_my_projects

        Then we are chillen

    """
    # just some temp data
    page_name = "MATCHSTATS"
    page_description = "MATCHSTATS"
    title = "MATCHSTATS"

    skill_match = {}
    matched_students = []
    interest_match = {}
    interest_reason_tuple = []
    cur_project = ''
    desired_skills = ''

    # create array of matched students
    print("project parameter:",project);
    print("project_match_list:", project_match_list)
    regex = r"<User: [^>]*>"
    reg_match = re.finditer(regex, project_match_list)
    for item in reg_match:
        print("reg_match:", item.group())
        username = item.group().split(": ")[1].replace(">","")
        matched_students.append(username)

    # find each students' known_skills that are desired by cur_project
    for stud in matched_students:
        student = get_object_or_404(User, username=stud)
        profile = Profile.objects.get(user=student)
        similar_skills = []

        projects = Project.get_my_projects(student)
        print("cur_project:",cur_project)
        print("get_my_projects(",student,"):", projects)

        if (len(projects) > 0):
            for k_skill in profile.known_skills.all():
                for p in projects:
                    print("p.title:",p.title,"project:",project)
                    if (p.title == project):
                        cur_project = p
                if (cur_project):
                    desired_skills = cur_project.desired_skills.all()

                for d_skill in desired_skills:

                    if (k_skill == d_skill):
                        similar_skills.append(k_skill)

        # interested = cur_project.interest.all()
        all_interests = Interest.objects.filter(project__in=projects)
        interests = all_interests.filter(user=student)
        # for inter in interests:
        #     print("stud:",stud,"interest: ",inter.interest_reason)

        # get newest entry
        if (len(interests) > 0):
            # print("len of interests", len(interests), "student:",stud)
            # print("len(inter)-1 -> reason", interests[len(interests)-1].interest_reason)
            interest_match[stud] = ([interests[len(interests)-1].interest, interests[len(interests)-1].interest_reason])
        else:
            interest_match[stud] = ([0, "Student hasn't showed interest, yet"])

        if (len(similar_skills) > 0):
            skill_match[stud] = similar_skills
        else:
            skill_match[stud] = ["No similar skills"]
        # interest_match[stud] = []
        # store dict with username as key
        # value = [interest, interest_reason]



    user = request.user
    print("=========================END MATCHSTATS=========================")

    return render(request, 'core/matchstats.html',{
        'skill_match':skill_match, 'project':project,
        'interest_reason_tuple':interest_reason_tuple,
        'user':user, 'interest_match':interest_match,
        })
