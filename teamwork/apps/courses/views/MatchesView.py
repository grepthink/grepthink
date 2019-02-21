from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User

from teamwork.apps.courses.models import Course, get_user_active_courses
from teamwork.apps.projects.models import Project, Membership
from teamwork.apps.profiles.models import Profile
from teamwork.apps.core.models import auto_ros, po_match

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
        courses = get_user_active_courses(request.user)
        for course in courses:
            for project in course.projects.all():
                p_match = po_match(project)
                project_match_list.extend([(course, project, p_match)])
            course_set.append(course)
    else:
        my_projects = Project.get_my_active_projects(request.user)

        for project in my_projects:
            p_match = po_match(project)
            project_match_list.extend([(project, p_match)])

    if request.POST.get('matchstats'):
        matches = request.POST.get('matchstats')

    return render(request, 'core/view_matches.html', {
        'project_match_list' : project_match_list, 'course_set': course_set, 'page_name': page_name,
            'page_description': page_description, 'title' : title})

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

        if (len(similar_skills) > 0):
            skill_match[stud] = similar_skills
        else:
            skill_match[stud] = ["No similar skills"]

    user = request.user

    return render(request, 'core/matchstats.html',{
        'page_name':page_name,'page_description':page_description,
        'title':title,'skill_match':skill_match, 'cur_project' : cur_project,
        'interest_match':interest_match
        })

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

    # needs some documentation/comments/more useful variable name for 'i'
    # what is auto/i and what is in i[1]?
    # why do we break if i[1]?
    flag = False
    for i in auto:
        if i[1]:
            flag = True
            break

    # Get just the projects so partial_project_box.html can loop through easily.
    # Will have to changes this once we get a better ui for autogen.
    projects = [i[0] for i in auto]

    return render(request, 'core/auto_gen.html', {
        'auto_gen' : auto, 'course': course, 'projects':projects, 'page_name': page_name,
            'page_description': page_description, 'title' : title, 'flag': flag})


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
