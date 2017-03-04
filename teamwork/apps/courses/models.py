from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from teamwork.apps.projects.models import *

import uuid
import random
import string
import datetime


# generates the add code
def rand_code(size):
    # usees a random choice from lowercase, uppercase, and digits
    return ''.join([random.choice(string.ascii_letters + string.digits) for i in range(size)])

# We need to update the User class to use django.auth
# from django.contrib.auth.models import User

# Model definitions for the core app.
# As we move forward, the core app will likely disapear. It's mainly for testing everything out right now.

class Course(models.Model):
    """
    Course: A database model (object) for courses.

    Fields:
        name: the name of the course.
        info: the course description
        term: the school term this course is offered
        students: many to many field of users
        slug: unique URL slug used to identify the project

        creator: the instructor of the course
        addCode: generated unique code used to enroll in the course

    Methods:
        __str__(self):                  Human readeable representation of the course object.
        save(self, *args, **kwargs):    Overides the default save operator...
        get_published():                Gets a list of all stored course objects.

    """
    # define the terms for the multiple choice
    Term_Choice = (
        ('Winter','Winter'),
        ('Spring', 'Spring'),
        ('Summer','Summer'),
        ('Fall','Fall'),
    )


    # The title of the course. Should not be null, but default is provided.
    name = models.CharField(max_length=255, default="No Course Title Provided")
    info = models.CharField(max_length=300, default="There is no Course Description")
    term = models.CharField(max_length=6, choices=Term_Choice,default='None')
    slug = models.CharField(max_length=20, unique=True)

    students = models.ManyToManyField(User, through='Enrollment')
    projects = models.ManyToManyField(Project)

    # auto fields
    creator = models.CharField(max_length=255, default="No admin lol")
    addCode = models.CharField(max_length=10, unique=True)
    # get the current date for the year
    now = datetime.datetime.now()
    year = models.CharField(max_length=20, default=now.year)
    professor = models.BooleanField(default = True)

    # The Meta class provides some extra information about the Project model.
    class Meta:
        # Verbose name is the same as class name in this case.
        verbose_name = "Course"
        # Multiple Project objects are referred to as Projects.
        verbose_name_plural = "Courses"

    def __str__(self):
        """
        Human readeable representation of the Project object. Might need to update when we add more attributes.
        Maybe something like, return u'%s %s' % (self.course, self.title)
        """
        return self.name + "(slug: " + self.slug + ")"

    def save(self, *args, **kwargs):
        """
        Overides the default save operator...
        Bassically a way to check if the Project object exists in the database. Will be helpful later.
        self.pk is the primary key of the Project object in the database!
        I don't know what super does...
        """

        # try catch to ensure the unique property is met
        try:
            # if the addcode has not been assigned yet get one
            if self.addCode is None or len(self.addCode) == 0:
                self.addCode = rand_code(10)

        except IntegrityError as e:
            # if we fail the unique property get a new addCode until one doesnt exist
            while Course.objects.filter(addCode=self.addCode).exists():
                self.addCode = rand_code(10)

        # Generate URL slug if not specified
        if self.slug is None or len(self.slug) == 0:
            newslug = self.name + "-" + self.term
            newslug = slugify(newslug)[0:20]
            while Course.objects.filter(slug=newslug).exists():
                newslug = self.name + "-" + self.term
                newslug = slugify(newslug[0:16] + "-" + rand_code(3))
            self.slug = newslug

        self.slug = slugify(self.slug)

        super(Course, self).save(*args, **kwargs)

    @staticmethod
    def get_published():
        """
        Gets a list of project objects. Used in views then passed to the template.
        """
        courses = Course.objects.filter()
        return courses

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=0)

    def __str__(self):
        """
        Human readeable representation of the Project object. Might need to update when we add more attributes.
        Maybe something like, return u'%s %s' % (self.course, self.title)
        """
        return self.course.name
