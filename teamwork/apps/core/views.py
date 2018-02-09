"""
Core views provide main site functionality.

"""
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from teamwork.apps.courses.models import *
from teamwork.apps.projects.models import *
from teamwork.apps.courses.views import *

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
                                                            'page_description': page_description, 'title': title})
    else:
        # Redirect user to login instead of public index (for ease of use)
        return render(request, 'core/login.html', {'page_name': page_name,
                                                   'page_description': page_description, 'title': title})


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
    logged_in = request.user.is_authenticated()

    if not logged_in:
        return render(request, 'core/landing.html', {'page_name': page_name,
                                                     'page_description': page_description, 'title': title})

    # If the user is a professor, return the dashboard html
    if logged_in and request.user.profile.isProf:
        page_name = "Dashboard"
        page_description = "Instructor Control Panel"
        title = "Dashboard"
        all_courses = Course.get_my_created_courses(request.user)
        return render(request, 'core/dashboard.html', {'page_name': page_name,
                                                       'page_description': page_description, 'title': title,
                                                       'all_courses': all_courses})

    if logged_in:
        page_name = "Timeline"
        page_description = "Recent Updates from Courses and Projects"
        title = "Timeline"
        if request.user.profile.isProf:
            all_courses = Course.get_my_created_courses(request.user)
        else:
            all_courses = Course.get_my_courses(request.user)
        date_updates = []
        for course in all_courses:
            course_updates = course.get_updates_by_date()
            date_updates.extend(course.get_updates_by_date())

    return render(request, 'core/index.html', {'page_name': page_name,
                                               'page_description': page_description, 'title': title,
                                               'date_updates': date_updates, 'logged_in': logged_in})



@login_required
def search(request):
    """
    This works but...

    If a user enters multiple search terms seperated by space,
    only the last keyword will return results
    - andgates
    """

    page_name = "Search"
    page_description = "Results"
    title = "Search Results"

    context = {'page_name': page_name,
               'page_description': page_description, 'title': title}

    if request.POST.get('q'):
        raw_keywords = request.POST.get('q')
        # print("Keywords:")
        # print(raw_keywords)

        keywords = []

        if raw_keywords is not None:
            if " " in raw_keywords:
                keywords = raw_keywords.split(" ")
            else:
                keywords.append(raw_keywords)
            for q in keywords:
                user_results = User.objects.filter(
                    Q(first_name__contains=q) |
                    Q(last_name__contains=q) |
                    Q(username__contains=q)).order_by('username')
                project_results = Project.objects.filter(
                    Q(title__contains=q) |
                    Q(content__contains=q) |
                    Q(tagline__contains=q)).order_by('title')
                course_results = Course.objects.filter(
                    Q(name__contains=q) |
                    Q(info__contains=q)).order_by('name')

            if user_results:
                context['user_results'] = user_results
            if project_results:
                context['project_results'] = project_results
            if course_results:
                context['course_results'] = course_results

    return render(request, 'core/search_results.html', context)


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
        # my_created = Project.get_created_projects(request.user)
        # projects = my_projects | my_created
        # projects = list(set(projects))
        for project in my_projects:
            p_match = po_match(project)
            project_match_list.extend([(project, p_match)])

    print("the method is:", request.method)
    if request.POST.get('matchstats'):
        matches = request.POST.get('matchstats')
        print("we are getting matchstats dude")

    return render(request, 'core/view_matches.html', {
        'project_match_list': project_match_list, 'course_set': course_set, 'page_name': page_name,
        'page_description': page_description, 'title': title})


@login_required
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

    flag = False
    for i in auto:
        if i[1]:
            flag = True
            break

    # Get just the projects so partial_project_box.html can loop through easily.
    # Will have to changes this once we get a better ui for autogen.
    projects = [x[0] for x in auto]

    return render(request, 'core/auto_gen.html', {
        'auto_gen': auto, 'course': course, 'projects': projects, 'page_name': page_name,
        'page_description': page_description, 'title': title, 'flag': flag})


def assign_auto(request, slug):
    """
    Assign the students to auto-gen teams
    """
    course = get_object_or_404(Course, slug=slug)
    auto = auto_ros(course)

    for p in auto:
        for mem in p[1]:
            Membership.objects.create(user=mem[0], project=p[0], invite_reason='')

    return redirect(auto_gen, course.slug)


@login_required
def matchstats(request, slug):
    """
        Displays why a user was matched with said project.
        Returns two dicts:
            -- skill_match:
                stores a user's skills that are similar with said projects'
                desired skills with their username as the key
            -- interest_match:
                Stores a users interest value and their reasoning for said project
                as a tuple with their username as the key

        TODO: could combine the two dicts if wanted.
    """

    # Page Information
    page_name = "Matchstats"
    page_description = "Stats on your matches"
    title = "Matchstats"

    matched_students = []
    skill_match = {}
    interest_match = {}

    cur_project = get_object_or_404(Project, slug=slug)
    cur_desiredSkills = cur_project.desired_skills.all()
    matched_students = po_match(cur_project)

    print("# of matched students:", len(matched_students))

    # match_list is a str object so parse it for usernames...
    # i'm sure theres a better way, couldn't pass the object
    # regex = r"<User: [^>]*>"
    # reg_match = re.finditer(regex, project_match_list)
    # for item in reg_match:
    #     username = item.group().split(": ")[1].replace(">","")
    #     matched_students.append(username)

    # find each students' known_skills that are desired by cur_project
    for stud, values in matched_students:

        student = get_object_or_404(User, username=stud)
        profile = Profile.objects.get(user=student)
        similar_skills = []

        for k_skill in profile.known_skills.all():

            for d_skill in cur_desiredSkills:

                if (k_skill == d_skill):
                    similar_skills.append(k_skill)

        all_interests = cur_project.interest.all()
        interests = all_interests.filter(user=student)

        for interest in interests:
            interest_match[stud] = ([interest, interest.interest_reason])

        if len(similar_skills) > 0:
            skill_match[stud] = similar_skills
        else:
            skill_match[stud] = ["No similar skills"]

    user = request.user

    return render(request, 'core/matchstats.html',{
        'page_name':page_name,'page_description':page_description,
        'title':title,'skill_match':skill_match, 'cur_project' : cur_project,
        'interest_match':interest_match
        })

def about(request):
    page_name = "Frequently Asked Questions"
    page_description = "GrepThink"
    title = "FAQ"
    return render(request, 'core/about.html', {'page_name': page_name,
        'page_description': page_description, 'title' : title})

def contact(request):
    """
    Renders the ContactUs page
    """
    return render(request, 'core/contact.html')
