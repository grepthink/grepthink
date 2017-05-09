from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

from teamwork.apps.courses.models import *
from teamwork.apps.projects.models import *



# profiles is already imported from projects, not necessary here


# send in the current list of
def sort(match):
    topScores = sorted(set(match.values()))
    matches = []
    for j in reversed(topScores):
        for u, i in match.items():
            if j == i:
                matches.append(u)
    return matches


"""
	Summary: this function is called to find matches for a project
	Params:
		project: the project looking for matches
		interestWeight: the weight the user can assign to interest, or default to 1
		knowWeight: the weight the user can assign to knowing a skill, or defaults to 1
		leanrWeight: the weight the user can assign to wanting to learn a skill, or default to 1
	returns: a list of the top users that match with a project, based on there cumulative score
		collected after each pass
"""


def po_match(project):
    initial = {}
    backup = {}

    # set weights based on criteria
    # locate project course
    course = next(course for course in Course.objects.all() if project in
            course.projects.all())
    if course.limit_weights:
        # print("po_match values overridden by course instructor")
        interestWeight = course.weigh_interest or 1
        knowWeight = course.weigh_know or 1
        learnWeight = course.weigh_learn or 1
    else:
        # dependency injection
        interestWeight = project.weigh_interest or course.weigh_interest or 1
        knowWeight = project.weigh_know or course.weigh_know or 1
        learnWeight = project.weigh_learn or course.weigh_learn or 1

    interested = project.interest.all()
    for i in interested:
        # generate the dictionary from the interest field, with the user's
        # rating as their initial score, mulitple by weight if given
        if i.user not in project.members.all() and project not in Project.get_created_projects(i.user):
            initial[i.user] = (i.interest * interestWeight)

    # Skill Matching
    # loop through the desired skills can check the skills table to see who
    # knows or wants to learn this skill. multiply by weight if necessary
    desired_skills = project.desired_skills.all()
    for i in desired_skills:
        know = i.known.all()
        for j in know:
            cur_course = Course.get_my_courses(j.user)
            # if is to allow for updating the score of users already counted
            if j.user not in project.members.all() and project not in Project.get_created_projects(j.user):
                if j.user in initial:
                    temp = initial[j.user]
                    temp += (2 * knowWeight)
                    initial[j.user] = temp
                # otherwise we add them to a backup list
                elif course in cur_course:
                    if j.user in backup:
                        temp = backup[j.user]
                        temp += (2 * knowWeight)
                        backup[j.user] = temp
                    else:
                        backup[j.user] = 2
        learn = i.learn.all()
        for k in learn:
            cur_course = Course.get_my_courses(j.user)
            if k.user not in project.members.all() and project not in Project.get_created_projects(k.user):
                if k.user in initial:
                    temp = initial[k.user]
                    temp += (1 * learnWeight)
                    initial[k.user] = temp
                # elif course in cur_course:
                    if k.user in backup:
                        temp = backup[k.user]
                        temp += (2 * learnWeight)
                        backup[k.user] = temp
                    else:
                        backup[k.user] = 2
    # we compare the size of the intial list to check if there are at least
    # 10 users that match already. If not we will add second list to the
    # intial to and for more users
    if len(set(initial.keys())) < 10:
        initial.update(backup)

    return sort(initial)
    # past classes match
    # scheduling match

def auto_ros(course, teamSize):
    match_list = []
    all_projects = course.projects.all()
    assigned = []
    roster = []

    # Get all the base matches for ALL projects
    for pro in all_projects:
        p_match = po_match(pro)
        match_list.extend([(pro, p_match, len(p_match))])

    # Sort the list of projects from least interest to most
    sorted_list = match_list.sort(key=lambda x: x[2])

    # Mark all curent memebers as assigned before assigning
    for z in match_list:
        for mem in z[0].members.all():
            assigned.append(mem)

    # Now Generate suggested rosters
    for x in match_list:
        temp_team = []
        # loop through the suggested members
        for y in range(0, x[2]):
            temp_user = x[1][y]
            # exit loop if the team is full
            if len(temp_team) == teamSize:
                break
            # skip the person if they have already been assigned
            elif (temp_user in assigned) or (temp_user in x[0].members.all()):
                continue
            # do the actually assignment
            else:
                # add the user to the suggested team
                temp_team.append(temp_user)
                # flag the user as assigned
                assigned.append(temp_user)
        # add the project and team to the roster
        roster.append([x[0], temp_team])
    for p in roster:
        for mem in p[1]:
            Membership.objects.create(user=mem, project=p[0], invite_reason='')
    return roster
