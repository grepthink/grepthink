from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

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
def po_match(project, interestWeight=1, knowWeight=1, learnWeight=1):
    initial = {}
    backup = {}
    # interest matching
    interested = project.interest.all()
    for i in interested:
        # generate the dictionary from the interest field, with the user's
        # rating as their initial score, mulitple by weight if given
        initial[i.user] = (i.interest * interestWeight)

    # Skill Matching
    # loop through the desired skills can check the skills table to see who
    # knows or wants to learn this skill. multiply by weight if necessary
    desired_skills = project.desired_skills.all()
    for i in desired_skills:
        know = i.known.all()
        for j in know:
            # if is to allow for updating the score of users already counted
            if j.user in initial:
                temp = initial[j.user]
                temp += (2 * knowWeight)
                initial[j.user] = temp
            # otherwise we add them to a backup list
            else:
                backup[j.user] = 2
        learn = i.learn.all()
        for k in learn:
            if k.user in initial:
                temp = initial[k.user]
                temp += (1 * learnWeight)
                initial[k.user] = temp
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
