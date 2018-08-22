from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

# Used for Email Address authentication method
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from teamwork.apps.courses.models import *
from teamwork.apps.projects.models import *
from teamwork.apps.projects.models import to_bits, from_bits

class EmailAddressAuthBackend(ModelBackend):
    """
    Authentication backend used to determine if a users email & password are valid.
    Returns:
        - None if Email doesn't exist or password doesn't match Email
        - UserModel object if email and password match
    """
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None

"""
    Summary: this function is called to sort the  list of matches by score
    Params:
       match: the list of matched students
    returns: a sorted list of students from best score to worst
"""
def sort(matchList):
    matches = []
    tagged = []
    topScores = sorted(matchList.values())
    for j in reversed(topScores):
        for u, i in matchList.items():
            if j == i and u not in tagged:
                matches.append((u,i))
                tagged.append(u)
    return matches


"""
    Summary: this function is called to find matches for a project
    Params:
        project: the project looking for matches
        interestWeight: the weight the user can assign to interest, or default to 1
        knowWeight: the weight the user can assign to knowing a skill, or defaults to 1
        learnWeight: the weight the user can assign to wanting to learn a skill, or default to 1
    returns: a list of the top users that match with a project, based on there cumulative score
        collected after each pass
"""
def po_match(project):
    initial = {}
    backup = {}

    # locate project course
    course = project.course.first()

    # set weights based on criteria
    if course.limit_weights:
        interestWeight = course.weigh_interest or 1
        knowWeight = course.weigh_know or 1
        learnWeight = course.weigh_learn or 1
    else:
        # dependency injection
        interestWeight = project.weigh_interest or course.weigh_interest or 1
        knowWeight = project.weigh_know or course.weigh_know or 1
        learnWeight = project.weigh_learn or course.weigh_learn or 1

    # Interest Matching
    interested = project.interest.all()
    for i in interested:
        # generate the dictionary from the interest field, with the user's
        # rating as their initial score, mulitple by weight if given
        # if they do not have a membership to a project in this course
        if not Membership.objects.filter(user=i.user, project__course=course):
            initial[i.user] = [(i.interest * interestWeight), (i.interest * interestWeight), 0, 0, 0]

    # Skill Matching
    # loop through the desired skills can check the skills table to see who
    # knows or wants to learn this skill. multiply by weight if necessary
    desired_skills = project.desired_skills.all()
    for i in desired_skills:
        # filter the users that know the skill to those actually in the course
        know = i.known.filter(user__enrollment__in=[course])

        for j in know:
            # if is to allow for updating the score of users already counted
            if Membership.objects.filter(user=j.user, project__course=course):
                continue
            # elif j.user in project.members.all() or project in Project.get_created_projects(j.user):
            #     continue
            else:
                if j.user in initial:
                    initial[j.user][0] += (2 * knowWeight)
                    initial[j.user][2] += (2 * knowWeight)
                # otherwise we add them to a backup list
                else:
                    if j.user in backup:
                        # temp += (2 * knowWeight)
                        backup[j.user][0] += (2 * knowWeight)
                        backup[j.user][2] += (2 * knowWeight)
                    else:
                        backup[j.user] = [(2 * knowWeight), 0, (2 * knowWeight), 0, 0]

        learn = i.learn.filter(user__enrollment__in=[course])
        for k in learn:
            # if is to allow for updating   the score of users already counted
            if Membership.objects.filter(user=k.user, project__course=course):
                continue
            # elif k.user in project.members.all() or project in Project.get_created_projects(k.user):
            #     continue
            else:
                if k.user in initial:
                    initial[k.user][0] += (1 * learnWeight)
                    initial[k.user][3] += (1 * learnWeight)
                else:
                    if k.user in backup:
                        backup[k.user][0] += (1 * learnWeight)
                        backup[k.user][3] += (1 * learnWeight)
                    else:
                        backup[k.user] = [(1 * learnWeight), 0, 0, (1 * learnWeight), 0]

    # we compare the size of the intial list to check if there are at least
    # 10 users that match already. If not we will add second list to the
    # intial to and for more users
    if len(set(initial.keys())) < 10:
        initial.update(backup)

    # Schedule Matching
    # Look through the currently selected students and reward those with the best schedule for
    # meeting with the current members
    for l in initial.keys():
        temp = by_schedule(l, project)
        initial[l][0] += temp
        initial[l][4] += temp

    return sort(initial)
    # past classes match

def auto_ros(course):
    match_list = []
    all_projects = course.projects.all()
    assigned = []
    roster = []

    # Get all the base matches for ALL projects
    for pro in all_projects:
        p_match = po_match(pro)
        match_list.extend([(pro, p_match, len(p_match))])

    # Sort the list of projects from least interest to most
    sorted_list = list(reversed(sorted(match_list, key=lambda x: x[-1])))

    # Mark all current members as 'assigned'
    for z in match_list:
        for mem in z[0].members.all():
            assigned.append(mem)

    # # Now Generate suggested rosters
    # for x in match_list:
    #     temp_team = []
    #     # loop through the suggested members
    #     for y in range(0, x[-1]):
    #         temp_user = x[1][y]
    #         # exit loop if the team is full
    #         if len(temp_team) + len(x[0].members.all()) == x[0].teamSize:
    #             break
    #         # skip the person if they have already been assigned
    #         elif temp_user[0] in assigned:
    #             continue
    #         # do the actually assignment
    #         else:
    #             # add the user to the suggested team
    #             temp_team.append(temp_user)
    #             # flag the user as assigned
    #             assigned.append(temp_user[0])
    #
    #     # add the project and team to the roster
    #     roster.append([x[0], temp_team])

    # Now Generate suggested rosters
    for x, y, z in sorted_list:
        temp_team = []

        # Add as many 4s and 5s first
        fives = [s for s in y if s[1][1] == 5]
        while(len(fives) > 0):
            pick = random.choice(fives)
            temp_user = pick[0]
            interest =x.interest.filter(user=temp_user).first()
            pick2 = [pick[0], pick[1], interest]

            # exit loop if the team is full
            if len(temp_team) + len(x.members.all()) == x.teamSize:
                break
            elif temp_user in assigned:
                fives.remove(pick)
            # do the actually assignment
            else:
                # add the user to the suggested team
                temp_team.append(pick2)
                assigned.append(temp_user)

        if len(temp_team) + len(x.members.all()) < x.teamSize:
            fours = [s for s in y if s[1][1] == 4]
            while(len(fours) > 0):
                pick = random.choice(fours)
                temp_user = pick[0]
                interest =x.interest.filter(user=temp_user).first()
                pick2 = [pick[0], pick[1], interest]

                # exit loop if the team is full
                if len(temp_team) + len(x.members.all()) == x.teamSize:
                    break
                elif temp_user in assigned:
                    fours.remove(pick)
                # do the actually assignment
                else:
                    # add the user to the suggested team
                    temp_team.append(pick2)
                    assigned.append(temp_user)

        #if the team still needs more add 3s
        if len(temp_team) + len(x.members.all()) < x.teamSize:
            threes = [s for s in y if s[1][1] == 3]
            while(len(threes) > 0):
                pick = random.choice(threes)
                temp_user = pick[0]
                interest = x.interest.filter(user=temp_user).first()
                pick2 = [pick[0], pick[1], interest]

                # exit loop if the team is full
                if len(temp_team) + len(x.members.all()) == x.teamSize:
                    break
                elif temp_user in assigned:
                    threes.remove(pick)
                # do the actually assignment
                else:
                    # add the user to the suggested team
                    temp_team.append(pick2)
                    assigned.append(temp_user)

        # add the project and team to the roster
        roster.append([x, temp_team])

    # Creates the membership objects, add the new students to respective teams
    # for p in roster:
    #     for mem in p[1]:
    #         Membership.objects.create(user=mem, project=p[0], invite_reason='')
    # print("roster:", roster)



    return sorted(roster, key=lambda x: x[0].title.lower())

def by_schedule(user, project):
    """
        Summary: Takes in a user and a project, compares users availability
            to the avalibility of other users in a specific project.
        Params: User - user object
                Project - Project object
        Returns: An integer that is floor(# meeting hours/ # pos meetings)
    """
    course = Course.objects.get(projects=project)

    event_list = []     # list of all events for each user
    pos_event = []      # list of possible meeting times
    sunday_list = []
    monday_list = []
    teusday_list = []
    wednesday_list = []
    thursday_list = []
    friday_list = []
    saturday_list = []
    total_hours = 0
    total_meetings = 0


    # Loops through each member
    for mem in project.members.all():
        # Loops through each event
        for event in mem.profile.avail.all():
            # adds to list
            event_list.append(event)

    # Adds potential members events
    for event in user.profile.avail.all():
        event_list.append(event)

    # Sorts each event into respective days
    for i in event_list:
        if i.day == "Sunday":
            sunday_list.append(i)
        if i.day == "Monday":
            monday_list.append(i)
        if i.day == "Teusday":
            teusday_list.append(i)
        if i.day == "Wednesday":
            wednesday_list.append(i)
        if i.day == "Thursday":
            thursday_list.append(i)
        if i.day == "Friday":
            friday_list.append(i)
        if i.day == "Saturday":
            saturday_list.append(i)

    # Converts to and from bitstring to find FREE time
    sunday_list = to_bits(sunday_list)
    sunday_list = from_bits(sunday_list)

    # Appends to list
    for i in sunday_list:
        pos_event.append(["Sunday", i[0], i[1], i[2], i[3]])
        total_hours = total_hours + (i[2] - i[0])

    monday_list = to_bits(monday_list)
    monday_list = from_bits(monday_list)
    for i in monday_list:
        pos_event.append(["Monday", i[0], i[1], i[2], i[3]])
        total_hours = total_hours + (i[2] - i[0])

    teusday_list = to_bits(teusday_list)
    teusday_list = from_bits(teusday_list)
    for i in teusday_list:
        pos_event.append(["Teusday", i[0], i[1], i[2], i[3]])
        total_hours = total_hours + (i[2] - i[0])

    wednesday_list = to_bits(wednesday_list)
    wednesday_list = from_bits(wednesday_list)
    for i in wednesday_list:
        pos_event.append(["Wednesday", i[0], i[1], i[2], i[3]])
        total_hours = total_hours + (i[2] - i[0])

    thursday_list = to_bits(thursday_list)
    thursday_list = from_bits(thursday_list)
    for i in thursday_list:
        pos_event.append(["Thursday", i[0], i[1], i[2], i[3]])
        total_hours = total_hours + (i[2] - i[0])

    friday_list = to_bits(friday_list)
    friday_list = from_bits(friday_list)
    for i in friday_list:
        pos_event.append(["Friday", i[0], i[1], i[2], i[3]])
        total_hours = total_hours + (i[2] - i[0])

    saturday_list = to_bits(saturday_list)
    saturday_list = from_bits(saturday_list)
    for i in saturday_list:
        pos_event.append(["Saturday", i[0], i[1], i[2], i[3]])
        total_hours = total_hours + (i[2] - i[0])

    total_meetings = len(pos_event)
    #print("\n\nStudent: %s\nMeeting List: %s\nHours: %d\nMeetings: %d\nHours/Meetings: %d\n\n"%(user.profile, pos_event, total_hours, total_meetings, total_hours/total_meetings))

    if total_meetings == 0:
        return 1
    return floor(total_hours/total_meetings)


# def by_schedule(user, project):
#     """
#         Summary: Takes in a user and a project, compares users availability
#             to the avalibility of other users in a specific project.
#         Params: User - user object
#                 Project - Project object
#         Returns: An integer that is floor(# meeting hours/ # pos meetings)
#     """
#     course = Course.objects.get(projects=project)
#     # low = project.lower_time_bound
#     # high = project.upper_time_bound
#
#     event_list = []     # list of all events for each user
#     pos_event = []      # list of possible meeting times
#     sunday_list = []
#     monday_list = []
#     teusday_list = []
#     wednesday_list = []
#     thursday_list = []
#     friday_list = []
#     saturday_list = []
#     total_hours = 0
#     total_meetings = 0
#
#
#     # Loops through each member
#     for mem in project.members.all():
#         # Loops through each event
#         for event in mem.profile.avail.all():
#             # adds to list
#             event_list.append(event)
#
#     # Adds potential members events
#     for event in user.profile.avail.all():
#         event_list.append(event)
#
#     # Sorts each event into respective days
#     for i in event_list:
#         if i.day == "Sunday":
#             sunday_list.append(i)
#         if i.day == "Monday":
#             monday_list.append(i)
#         if i.day == "Teusday":
#             teusday_list.append(i)
#         if i.day == "Wednesday":
#             wednesday_list.append(i)
#         if i.day == "Thursday":
#             thursday_list.append(i)
#         if i.day == "Friday":
#             friday_list.append(i)
#         if i.day == "Saturday":
#             saturday_list.append(i)
#
#     # Converts to and from bitstring to find FREE time
#     sunday_list = to_bits(sunday_list, low, high)  #this is working
#     sunday_list = from_bits(sunday_list)    #this is now working
#     # Appends to list
#     for i in sunday_list:
#         pos_event.append(["Sunday", i[0], i[1], i[2], i[3]])
#         total_hours = total_hours + (i[2] - i[0])
#
#     monday_list = to_bits(monday_list, low, high)
#     monday_list = from_bits(monday_list)
#     for i in monday_list:
#         pos_event.append(["Monday", i[0], i[1], i[2], i[3]])
#         total_hours = total_hours + (i[2] - i[0])
#
#     teusday_list = to_bits(teusday_list, low, high)
#     teusday_list = from_bits(teusday_list)
#     for i in teusday_list:
#         pos_event.append(["Teusday", i[0], i[1], i[2], i[3]])
#         total_hours = total_hours + (i[2] - i[0])
#
#     wednesday_list = to_bits(wednesday_list, low, high)
#     wednesday_list = from_bits(wednesday_list)
#     for i in wednesday_list:
#         pos_event.append(["Wednesday", i[0], i[1], i[2], i[3]])
#         total_hours = total_hours + (i[2] - i[0])
#
#     thursday_list = to_bits(thursday_list, low, high)
#     thursday_list = from_bits(thursday_list)
#     for i in thursday_list:
#         pos_event.append(["Thursday", i[0], i[1], i[2], i[3]])
#         total_hours = total_hours + (i[2] - i[0])
#
#     friday_list = to_bits(friday_list, low, high)
#     friday_list = from_bits(friday_list)
#     for i in friday_list:
#         pos_event.append(["Friday", i[0], i[1], i[2], i[3]])
#         total_hours = total_hours + (i[2] - i[0])
#
#     saturday_list = to_bits(saturday_list, low, high)
#     saturday_list = from_bits(saturday_list)
#     for i in saturday_list:
#         pos_event.append(["Saturday", i[0], i[1], i[2], i[3]])
#         total_hours = total_hours + (i[2] - i[0])
#
#     total_meetings = len(pos_event)
#     #print("\n\nStudent: %s\nMeeting List: %s\nHours: %d\nMeetings: %d\nHours/Meetings: %d\n\n"%(user.profile, pos_event, total_hours, total_meetings, total_hours/total_meetings))
#
#     if total_meetings == 0:
#         return 1
#     return floor(total_hours/total_meetings)
