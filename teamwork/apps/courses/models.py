from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

import uuid
import random
import string

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
    COurse: A database model (object) for courses.

    Fields:
        name: the name of the course.

    Methods:
        __str__(self):                  Human readeable representation of the course object.
        save(self, *args, **kwargs):    Overides the default save operator...
        get_published():                Gets a list of all stored course objects.

    """

    # The title of the course. Should not be null, but default is provided.
    name = models.CharField(max_length=255, default="No Course Title Provided")
    students = models.ManyToManyField(User, through='Enrollment')

    # auto fields
    creator = models.CharField(max_length=255, default="No admin lol")
    
    # this is option 2 using a UUID, but long and has hyphens
    # addCode = models.CharField(max_length=8, unique=True, default=uuid.uuid4)
    # short solution using a random alphanumeric generator
    addCode = models.CharField(max_length=10, unique=True)    



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
        return self.name

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
            save()
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
