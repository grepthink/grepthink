"""
Teamwork: projects

Database Models for the objects: Project, Membership, Interest, ProjectUpdate
"""

# Built-in modules
from __future__ import unicode_literals

import random
from datetime import date
import datetime
import string
from math import floor
from decimal import Decimal

# Third-party Modules
import markdown
# Django modules
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
# Not used currently
from django.db.models import Q
from django.template.defaultfilters import slugify

from django.core.validators import URLValidator

from django.utils import timezone

from teamwork.apps.core.models import *
from teamwork.apps.profiles.models import *

# Generates add code
def rand_code(size):
    # Usees a random choice from lowercase, uppercase, and digits
    return ''.join([
        random.choice(string.ascii_letters + string.digits) for i in range(size)
    ])

# Model definitions for the core app.
# As we move forward, the core app will likely disapear. It's mainly for testing everything out right now.
class Interest(models.Model):
    """
    Interest object relates a user to a interest (may be changed in the future)
    """
    # can access interest from the user through user.interest.all()
    user = models.ForeignKey(User, related_name='interest', on_delete=models.CASCADE)
    interest = models.PositiveIntegerField()
    interest_reason = models.CharField(max_length=100)

    def __str__(self):
        return("%d - %s: %s"%(self.interest, self.user.username, self.interest_reason))

class Tsr(models.Model):
    """
    TSR objects relate a user and tsr fields, along with assignment information
    """
    # number of the TSR assignment form was submitted for
    ass_number = models.DecimalField(max_digits=2, decimal_places=0, default=1)
    # person who is evaluating
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE,
        related_name="evaluator", default=0)
    # person being evaluated
    evaluatee = models.ForeignKey(User, on_delete=models.CASCADE,
        related_name="evaluatee", default=0)
    # sprint percent contribution
    percent_contribution = models.DecimalField(max_digits=2, decimal_places=0)
    # evaluatee pros
    positive_feedback = models.CharField(max_length=255, default='')
    # evaluatee cons
    negative_feedback = models.CharField(max_length=255, default='')
    # scrum input only
    tasks_completed = models.CharField(max_length=255, default='')
    # scrum input only
    performance_assessment = models.CharField(max_length=255, default='')
    # scrum input only
    notes = models.CharField(max_length=255, default='')
    # soft deadline fix
    late = models.BooleanField(default=False)
    # Unique URL slug for assignment
    slug = models.CharField(
        default="",
        max_length=20,
        unique=True)

    def __str__(self):
        return(("%d, %s, %s, %d, %s, %s, %s, %s, %s"%(self.ass_number, self.evaluator.email, self.evaluatee.email, self.percent_contribution,
            self.positive_feedback, self.negative_feedback,
            self.tasks_completed, self.performance_assessment, self.notes)))
    def save(self, *args, **kwargs):
        # Generate URL slug if not specified
        if self.slug is None or len(self.slug) == 0:
            newslug = rand_code(10)
            while Tsr.objects.filter(slug=newslug).exists():
                newslug = rand_code(10)
            self.slug = newslug

        super(Tsr, self).save(*args, **kwargs)

class Techs(models.Model):
    """
    Skills: A database model (object) for skills.
    Fields:
        skill: a field that contains the name of a skill
    Methods:
        __str__(self):                  Human readeable representation of the skill object.
        save(self, *args, **kwargs):    Overides the default save operator...
        """
    # skill, a string
    tech = models.CharField(max_length=255,default="")

    def __str__(self):
        return self.tech
    class Meta:
        # Verbose name is the same as class name in this case.
        verbose_name = "Tech"
        # Multiple Skill objects are referred to as Projects.
        verbose_name_plural = "Techs"
        ordering = ('tech',)

    def save(self, *args, **kwargs):
        """
        Overides the default save operator...
        Bassically a way to check if the Project object exists in the database. Will be helpful later.
        self.pk is the primary key of the Project object in the database!
        I don't know what super does...
        """
        super(Techs, self).save(*args, **kwargs)

class Project(models.Model):
    """
    Project: A database model (object) for projects.

    Fields:
        title: the title of the project.

    Methods:
        __str__(self):                  Human readeable representation of the Project object.
        save(self, *args, **kwargs):    Overides the default save operator...
        get_published():                Gets a list of all stored Project objects.

    """

    Lower_Boundary_Choice = ((0, 'No Preference'), (2, '01:00'), (4, '02:00'), (6, '03:00'),
                       (8, '04:00'), (10, '05:00'), (12, '06:00'), (14, '07:00'),
                       (16, '08:00'), (18, '09:00'), (20, '10:00'), (22, '11:00'),
                       (24, '12:00'), )

    Upper_Boundary_Choice = ((48, 'No Preference'), (26, '13:00'), (28, '14:00'), (30, '15:00'),
                       (32, '16:00'), (34, '17:00'), (36, '18:00'), (38, '19:00'),
                       (40, '20:00'), (42, '21:00'), (44, '22:00'), (46, '23:00'), )

    # The title of the project. Should not be null, but default is provided.
    title = models.CharField(
        max_length=255,
        default="No Project Title Provided")

    # creator of a course with a FK to that User object
    # The Fk with generate a set of course object for that user
    creator = models.ForeignKey(
        User,
        # students can access courses through this relation
        # user.creator.all()
        related_name='project_creator',
        on_delete=models.CASCADE)

    # scrum master of the project with a FK to that User object
    scrum_master = models.ForeignKey(
        User,
        related_name='scrum_master',
        on_delete=models.CASCADE,
        blank=True,
        null=True)

    # Short project description
    tagline = models.TextField(
        max_length=38,
        default="Default Project Tagline")

    # Verbose project description.
    content = models.TextField(
        max_length=4000,
        default="Content")

    # Members associated with a project (Membership objects)
    members = models.ManyToManyField(
        User,
        related_name='membership',
        through='Membership')

    no_request = models.BooleanField(default=False)

    # Pending Members that have request to Join the project
    pending_members = models.ManyToManyField(
        User,
        related_name='pending',
        default="")

    # Pending members that have been invited to join the project
    pending_invitations = models.ManyToManyField(
        User,
        related_name='invitations',
        default="")

    # TA assigned to the project
    ta = models.ForeignKey(
        User,
        related_name='ta',
        on_delete=models.CASCADE,
        blank=True,
        null=True)

    # Location of Weekly meeting with TA
    ta_location = models.TextField(
        max_length=38,
        default="")

    # Time of Weekly meeting with TA
    ta_time = models.TextField(
        max_length=38,
        default="")

    # Project's Assigned Teacher Assistant
    assigned_ta = models.ManyToManyField(
        User,
        related_name='assigned_ta',
        default="")

    # TODO:
    # scrum_schedule
    # github_link

    # Skills needed for the project.
    desired_skills = models.ManyToManyField(
        Skills,
        related_name="desired",
        default="")
#---------------------------------------------------------------------------------
    desired_techs = models.ManyToManyField(
        Techs,
        related_name="technologies",
        default="")
#----------------------------------------------------------------------------------
    # True when the proejct is accepting new members. False when project is full.
    avail_mem = models.BooleanField(
        default=True)

    # True when project is sponsered. False when project is not sponsered. Field hidden to students.
    sponsor = models.BooleanField(
        default=False)

    # Unique URL slug for project
    slug = models.CharField(
        max_length=20,
        unique=True)

    project_image = models.TextField(
        max_length=100,
        default='http://i.imgur.com/5Z17VfH.png')



    # TODO:NEED TO SETUP M2M not proper
    # Resource list that the project members can update
    resource = models.TextField(
        max_length=4000,
        default="*No resources provided*")

    # TODO:NEED UPDATES M2M for proper link not query
    # the interest in a project can be access through back relationship
    # project.interested.all()
    interest = models.ManyToManyField(
        Interest,
        related_name='project_interest',
        default=None)

    # TODO:NEED TO GET THIS GOING AS WELL FOR NAV FILTERS
    # Date the project was originally submitted on
    # Commented until we get to a point where we want to have everyone flush
    #create_date = models.DateTimeField(auto_now_add=True)

    # projects tsr
    tsr = models.ManyToManyField(
        Tsr,
        related_name='project_tsr',
        default=None)

    # Store the teamSize for team generation and auto switch accepting members
    teamSize = models.IntegerField(
        default=4)

    # meetings - Availabiliy as an ajax string
    meetings = models.TextField(
        default='')
    readable_meetings = models.TextField(
        null=True)

    # Project weight for matching unless inputed
    weigh_interest = models.IntegerField(
        default=1)
    weigh_know = models.IntegerField(
        default=1)
    weigh_learn = models.IntegerField(
        default=1)

    # The Meta class provides some extra information about the Project model.
    class Meta:
        # Verbose name is the same as class name in this case.
        verbose_name = "Project"
        # Multiple Project objects are referred to as Projects.
        verbose_name_plural = "Projects"

    def __str__(self):
        """
        Human readeable representation of the Project object. Might need to update when we add more attributes.
        Maybe something like, return u'%s %s' % (self.course, self.title)
        """
        # mem = ""
        # for m in self.members.all():
        #     mem += "\t%s\n"%(m.username)

        # info = "Title: %s\nCreator: %s\nMembers: \n%sAccepting? %s\nSponsor: %s\nSlug: %s\n"%(self.title, self.creator.username, mem, self.avail_mem, self.sponsor, self.slug)
        return self.title

    def save(self, *args, **kwargs):
        """
        Overides the default save operator...
        Bassically a way to check if the Project object exists in the database. Will be helpful later.
        self.pk is the primary key of the Project object in the database!
        """
        #if not self.pk:
        #    super(Project, self).save(*args, **kwargs)

        # Generate a Project URL slug if not specified
        #     Based off Courses.save URL slug written by August
        if self.slug is None or len(self.slug) == 0:
            # Basing the slug off of project title. Possibly change in the future.
            newslug = self.title
            newslug = slugify(newslug)[0:20]
            while Project.objects.filter(slug=newslug).exists():
                #print(Project.objects.filter(slug=newslug).exists())
                newslug = self.title
                newslug = slugify(newslug[0:16] + "-" + rand_code(3))
            self.slug = newslug

            self.slug = slugify(self.slug)

        super(Project, self).save(*args, **kwargs)

    """
    Gets all students in a project and returns a list
    """
    def get_members(self):
        temp = self.members.all()
        students = []

        for stud in temp:
            students.append(stud)

        return students

    # Generates a list of possible avalibilities and stores in current project's avalibiltiy
    def generate_avail(self):
        event_list = []     # list of all events for each user
        pos_event = []      # list of possible meeting times
        temp = []

        sunday_list = []

        monday_list = []

        teusday_list = []

        wednesday_list = []

        thursday_list = []

        friday_list = []

        saturday_list = []

        # Loops through each member
        for user in self.members.all():
            # Loops through each event
            for event in user.profile.avail.all():
                # adds to list
                event_list.append(event)

        # Sorts each event into respective days
        for i in event_list:
            if i.day == "Sunday":
                sunday_list.append(i)
            if i.day == "Monday":
                monday_list.append(i)
            if i.day == "Tuesday":
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
        sunday_list = to_bits(sunday_list)  #this is working
        sunday_list = from_bits(sunday_list)    #this is now working
        # Appends to list
        for i in sunday_list:
            pos_event.append(["Sunday", i[0], i[1], i[2], i[3]])

        monday_list = to_bits(monday_list)
        monday_list = from_bits(monday_list)
        for i in monday_list:
            pos_event.append(["Monday", i[0], i[1], i[2], i[3]])

        # "TEU-SDAY"
        teusday_list = to_bits(teusday_list)
        teusday_list = from_bits(teusday_list)
        for i in teusday_list:
            pos_event.append(["Teusday", i[0], i[1], i[2], i[3]])

        wednesday_list = to_bits(wednesday_list)
        wednesday_list = from_bits(wednesday_list)
        for i in wednesday_list:
            pos_event.append(["Wednesday", i[0], i[1], i[2], i[3]])

        thursday_list = to_bits(thursday_list)
        thursday_list = from_bits(thursday_list)
        for i in thursday_list:
            pos_event.append(["Thursday", i[0], i[1], i[2], i[3]])

        friday_list = to_bits(friday_list)
        friday_list = from_bits(friday_list)
        for i in friday_list:
            pos_event.append(["Friday", i[0], i[1], i[2], i[3]])

        saturday_list = to_bits(saturday_list)
        saturday_list = from_bits(saturday_list)
        for i in saturday_list:
            pos_event.append(["Saturday", i[0], i[1], i[2], i[3]])

        # Returns list of possible events

        ajax = []
        for i in range(len(pos_event)):
            # d is a dictionary
            d = {}
            d['start'] = '%s%02d:%02d:00'%(dayasday(pos_event[i][0]), pos_event[i][1], pos_event[i][2])
            d['end'] = '%s%02d:%02d:00'%(dayasday(pos_event[i][0]), pos_event[i][3], pos_event[i][4])
            d['title'] = 'Meeting'
            # appends dictionary to list
            ajax.append(d)

        # returns list of dictionaries
        return ajax

    @staticmethod
    def get_my_projects(user):
        """
        Gets a list of project objects. Used in views then passed to the template.
        """
        # #Gets membership object of current user
        # myProjects = Membership.objects.filter(user=user)
        # #Gets project queryset of only projects user is in OR the user created
        # proj = Project.objects.filter(membership__in=myProjects)

        mem = list(user.membership.all())

        claimed = list(user.ta.all())

        created = list(user.project_creator.all())

        projects = list(set(mem + created + claimed))

        return projects

    @staticmethod
    def get_my_active_projects(user):
        """
        Gets a list of project objects. Used in views then passed to the template.
        """
        # #Gets membership object of current user
        # myProjects = Membership.objects.filter(user=user)
        # #Gets project queryset of only projects user is in OR the user created
        # proj = Project.objects.filter(membership__in=myProjects)

        mem = list(user.membership.filter(course__disable=False))

        claimed = list(user.ta.filter(course__disable=False))

        created = list(user.project_creator.filter(course__disable=False))

        projects = list(set(mem + created + claimed))

        return projects

    @staticmethod
    def get_my_disabled_projects(user):
        """
        Gets a list of project objects. Used in views then passed to the template.
        """
        # #Gets membership object of current user
        # myProjects = Membership.objects.filter(user=user)
        # #Gets project queryset of only projects user is in OR the user created
        # proj = Project.objects.filter(membership__in=myProjects)

        mem = list(user.membership.filter(course__disable=True))

        claimed = list(user.ta.filter(course__disable=True))

        created = list(user.project_creator.filter(course__disable=True))

        projects = list(set(mem + created + claimed))

        return projects

    @staticmethod
    def get_all_projects():
        """
        Gets a list of project objects. Used in views then passed to the template.
        """
        projects = Project.objects.all()
        return projects

    @staticmethod
    def get_created_projects(user):
        """
        Gets a list of porject objects that the user created. Used in views then passed to the template
        """
        # proj = Project.objects.filter(creator=user.username)

        proj = user.project_creator.all()

        return proj

    def get_content_as_markdown(self):
        return markdown.markdown(self.content, safe_mode='escape')

    def get_resource_as_markdown(self):
        return markdown.markdown(self.resource, safe_mode='escape')

    def get_updates(self):
        return ProjectUpdate.objects.filter(project=self).prefetch_related('project', 'user')

    def get_resources(self):
        return ResourceUpdate.objects.filter(project=self).prefetch_related('project', 'user')

    def get_chat(self):
        return self.chat.all()

    """ Unfortunately not possible due to dependency loop
    def course(self):
        return next(course for course in Course.objects.all() if this in
                course.projects.all())
    """

class Membership(models.Model):
    """
    Membership objects relate a user and a project.
    """
    user = models.ForeignKey(
        User,
        related_name='membershipUser',
        on_delete=models.CASCADE,
        default=0)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        default=0)
    invite_reason = models.CharField(
        max_length=64)

    def __str__(self):
        return("%s: %s"%(self.user.username, self.project.title))
#-----------------------------------------------------------------------



class ProjectUpdate(models.Model):
    """
    ProjectUpdate objects are updates associated with a project

    Attributes:
        project: ForeignKey to the project, found by project slug
        update_title: The title of a project update
        update: The content of the project update
        date: Date that the project update was posted
        user: The currently logged in user (associated with the project update)

    """
    project = models.ForeignKey(Project)
    update_title = models.CharField(
        max_length=255, default="Default Update Title")
    update = models.TextField(max_length=2000, default="Default Update")
    date = models.DateTimeField(editable=True)
    user = models.ForeignKey(User)

    class Meta:
        verbose_name = "Project Update"
        verbose_name_plural = "Project Updates"
        ordering = ("-date", )

    def __str__(self):
        return '{0} - {1}'.format(self.user.username, self.project.title)

    def save(self, *args, **kwargs):
        """
        Overrides default save
        """
        self.date = datetime.datetime.now()

        super(ProjectUpdate, self).save(*args, **kwargs)

class ResourceUpdate(models.Model):

    project = models.ForeignKey(Project)
    date = models.DateTimeField(editable=True)
    user = models.ForeignKey(User)
    src_title = models.CharField(max_length=255, default="Default Resource Title")
    src_link = models.URLField(max_length=2000, default="Default Resource Link")

    class Meta:
        verbose_name = "Resource Update"
        verbose_name_plural = "Resource Updates"
        ordering = ("-date", )

    def __str__(self):
        return '{0} - {1}'.format(self.user.username, self.project.title)

    def save(self, *args, **kwargs):
        """
        Overrides default save
        """
        self.date = datetime.datetime.now()

        super(ResourceUpdate, self).save(*args, **kwargs)

class ProjectChat(models.Model):

    project = models.ForeignKey(Project, related_name='chat', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='author_chat', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, editable=True)
    content = models.CharField(max_length=2000, default="")

    class Meta:
        verbose_name = "Project Chat"
        ordering = ("-date", )

    def __str__(self):
        return '{0} - {1}'.format(self.author.username, self.content)

# Generates add code
def rand_code(size):
    # Usees a random choice from lowercase, uppercase, and digits
    return ''.join([
        random.choice(string.ascii_letters + string.digits) for i in range(size)
    ])

# Converts a number into a weekday
def dayofweek(number):
    return {
        9: "Sunday",
        10: "Monday",
        11: "Tuesday",
        12: "Wednesday",
        13: "Thursday",
        14: "Friday",
        15: "Saturday",
    }.get(number, "Day that doesnt exist")

def dayasday(day):
    return {
        "Sunday": '2017-04-09T',
        "Monday": '2017-04-10T',
        "Teusday": '2017-04-11T',
        "Wednesday": '2017-04-12T',
        "Thursday": '2017-04-13T',
        "Friday": '2017-04-14T',
        "Saturday": '2017-04-15T',
    }.get(day, '2017-04-00T')

# Given an array, creates a bitstring based on meeting times
def to_bits(day):
    # Creates array of all 0's of length 48
    bitstring = [False]*48
    # Loops through each Event in array
    for event in day:
        # Start = double start hour (30 min intervals)
        start = 2*event.start_time_hour
        # End = double End hour (30 min intervals)
        end = 2*event.end_time_hour

        # SPECIAL CASE: Because 12a == 0, we manually set end to 47
        if event.end_time_hour == 0:
            end = 47


        for i in range (start, end+1):
            bitstring[i] = True
        # If we ended in XX:30, block off next bit
        if event.end_time_min == 30:
            bitstring[end+1] = True


    # Manually block off time bounds given by professor
    for x in range(0, 16):
        bitstring[x] = True
    for x in range(44, 48):
        bitstring[x] = True

    return bitstring

#given a bitstring, converts to array containing start and end time
def from_bits(bitstring):
    event_array = []
    temp = 0
    start_hour = 0
    start_min = 0
    end_hour = 0
    end_minute = 0

    i = 0
    # For each index in bitstring
    while i < len(bitstring):
        # If current index is False (Free)
        if bitstring[i] is False:
            # If odd, start at xx:30
            if i % 2 != 0:
                start_min = 30
            # Start hour is i/2
            start_hour = floor(i/2)

            # Loops until True (Busy)
            temp = i
            while bitstring[temp] == False:
                # If next element is True (Busy), we are at end of time slot

                # Getting out of range Here
                # What to do if last element in array?
                if temp == len(bitstring) - 1:
                    # Update i
                    i = temp
                    # If odd, end at xx:30
                    if i % 2 != 0:
                        end_min = 30
                    # End hour is i/2
                    end_hour = floor(i/2)
                    break

                elif bitstring[temp + 1] == True:
                    # Update i
                    i = temp
                    # If odd, end at xx:30
                    if i % 2 != 0:
                        end_min = 30
                    # End hour is i/2
                    end_hour = floor(i/2)
                    break

                # Increase temp
                temp += 1

            # Add event to array
            event_array.append([start_hour, start_min, end_hour, end_min])

        # Update iterator
        i=i+1

    return event_array
