"""
Teamwork: projects

Database Models for the objects, Project, Membership, Intrest, ProjectUpdate
"""

# Built-in modules
from __future__ import unicode_literals
from datetime import datetime
import random
import string

# Django modules
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# Not used currently
from django.db.models import Q

# Third-party Modules
import markdown

# Local Modules
from teamwork.apps.profiles.models import *

# Generates add code
def rand_code(size):
    # Usees a random choice from lowercase, uppercase, and digits
    return ''.join([random.choice(string.ascii_letters + string.digits) for i in range(size)])

# Model definitions for the core app.
# As we move forward, the core app will likely disapear. It's mainly for testing everything out right now.
class Interest(models.Model):
    """
    Intrest object relates a user to a intrest (may be changed in the future)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interest = models.PositiveIntegerField()
    interest_reason = models.CharField(max_length=100)

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

    # The title of the project. Should not be null, but default is provided.
    title = models.CharField(max_length=255, default="No Project Title Provided")
    # TODO: This should not be a CharField
    creator = models.CharField(max_length=255, default="No Creator (Weird)")
    # Verbose project description.
    content = models.TextField(max_length=4000, default="Content")
    # Members associated with a project (Membership objects)
    members = models.ManyToManyField(User, through='Membership')
    # Skills needed for the project.
    desired_skills = models.ManyToManyField(Skills, related_name="desired", default="")
    # True when the proejct is accepting new members. False when project is full.
    avail_mem = models.BooleanField(default = True)
    # True when project is sponsered. False when project is not sponsered. Field hidden to students.
    sponsor = models.BooleanField(default = False)
    # Unique URL slug for project
    slug = models.CharField(max_length=20, unique=True)
    # Resource list that the project members can update
    resource = models.TextField(max_length=4000)

    interest = models.ManyToManyField(Interest, default = '')
    # Date the project was originally submitted on
    # Commented until we get to a point where we want to have everyone flush
    #create_date = models.DateTimeField(auto_now_add=True)


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
                print(Project.objects.filter(slug=newslug).exists())
                newslug = self.title
                newslug = slugify(newslug[0:16] + "-" + rand_code(3))
            self.slug = newslug

        self.slug = slugify(self.slug)

        super(Project, self).save(*args, **kwargs)

    @staticmethod
    def get_my_projects(user):
        """
        Gets a list of project objects. Used in views then passed to the template.
        """
        #Gets membership object of current user
        myProjects = Membership.objects.filter(user=user)
        #Gets project queryset of only projects user is in OR the user created
        #BUG: if creator not in project, they cannot see project
        proj = Project.objects.filter(membership__in=myProjects)

        print(proj)
        return proj

    def get_all_projects():
        """
        Gets a list of project objects. Used in views then passed to the template.
        """
        projects = Project.objects.filter()
        return projects

    def get_content_as_markdown(self):
        return markdown.markdown(self.content, safe_mode='escape')

    def get_updates(self):
        return ProjectUpdate.objects.filter(project=self)

class Membership(models.Model):
    """
    Membership objects relate a user and a project.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=0)
    invite_reason = models.CharField(max_length=64)


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
    update_title = models.CharField(max_length=255, default="Default Update Title")
    update = models.TextField(max_length=2000, default="Default Update")
    date = models.DateTimeField(auto_now_add=True, editable=True)
    user = models.ForeignKey(User)

    class Meta:
        verbose_name = "Project Update"
        verbose_name_plural = "Project Updates"
        ordering = ("-date",)

    def __str__(self):
        return '{0} - {1}'.format(self.user.username, self.project.title)

# project status: open/closed and number available
# currently commented to avoid conflict with other files
"""
class Project_Status (Project):

    #numerical ranges for number of members in a group
    SIX = 6
    FIVE = 5
    FOUR = 4
    THREE = 3
    TWO = 2
    ONE = 1
    ZERO = 0
    MAX_CHOICES = (
        (SIX,'Six'),
        (FIVE,'Five'),
    )
    NUM_CHOICES = (
        (FIVE,'Five'),
        (FOUR,'Four'),
        (THREE,'Three'),
        (TWO,'Two'),
        (ONE,'One'),
        (ZERO,'Zero'),
    )

    # max_cap = maximum number of members in a group
    # current_mem = number of members currently in a group
    # need_mem = number of members needed in a group
    # avail_mem = determine open/closed status of a project
    max_cap = models.PositiveIntegerField(choices = MAX_CHOICES)PositiveIntegerField
    current_mem = models.PositiveIntegerField(default = 1, choices = NUM_CHOICES)
    need_mem = models.PositiveIntegerField(choices = NUM_CHOICES)
    avail_mem = models.BooleanField(default = True)

    def remain(self):
        self.need_mem = {{self.max_cap|sub: self.current_mem}}
        self.avail_mem = case(when(self.need_mem = 0, then = False))

"""
