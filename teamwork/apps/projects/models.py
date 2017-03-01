from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# We need to update the User class to use django.auth
# from django.contrib.auth.models import User

# Model definitions for the core app.
# As we move forward, the core app will likely disapear. It's mainly for testing everything out right now.

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
    creator = models.CharField(max_length=255, default="No Creator (Weird)")

    members = models.ManyToManyField(User, through='Membership')

    avail_mem = models.BooleanField(default = True)
    sponsor = models.BooleanField(default = False)


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
        I don't know what super does...
        """
        if not self.pk:
            super(Project, self).save(*args, **kwargs)
        super(Project, self).save(*args, **kwargs)

    @staticmethod
    def get_published():
        """
        Gets a list of project objects. Used in views then passed to the template.
        """
        projects = Project.objects.filter()
        return projects

class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=0)
    invite_reason = models.CharField(max_length=64)

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





# Legacy code for me to sort through next and slowly add back in:

"""
class Project(models.Model):
#Authors is a is a forign key from class User.
#Each project object is associated with authors (current_members).

    # Authors
    #authors = models.ForeignKey(User, related_name='+')
    # all many to many fields first, to easily identify relationships
    #course = models.ManyToManyField(Course, related_name="course_id")
    #project_owner = models.ManyToManyField(User, related_name="po")
    project_owner = models.ForeignKey(User)
    #current_members = models.ManyToManyField(User, related_name="members")
    #project_owner = models.ManyToManyField(User, related_name="po")
    project_name = models.CharField(max_length=50, default="")
    project_info = models.CharField(max_length=100, default="")
    #create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_name
"""
