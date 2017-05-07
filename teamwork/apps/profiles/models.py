"""
Teamwork: profiles

Database Models for the objects: Skills, Profile
"""

# Django Imports
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models.signals import post_save
from django.dispatch import receiver

class Skills(models.Model):
    """
    Skills: A database model (object) for skills.

    Fields:
        skill: a field that contains the name of a skill

    Methods:
        __str__(self):                  Human readeable representation of the skill object.
        save(self, *args, **kwargs):    Overides the default save operator...

        """
    # skill, a string
    skill = models.CharField(max_length=255,default="")

    def __str__(self):
        return self.skill
    class Meta:
        # Verbose name is the same as class name in this case.
        verbose_name = "Skill"
        # Multiple Skill objects are referred to as Projects.
        verbose_name_plural = "Skills"
        ordering = ('skill',)

    def save(self, *args, **kwargs):
        """
        Overides the default save operator...
        Bassically a way to check if the Project object exists in the database. Will be helpful later.
        self.pk is the primary key of the Project object in the database!
        I don't know what super does...
        """
        super(Skills, self).save(*args, **kwargs)

# Converts a number into a weekday
def dayofweek(number):
    return {
        9: "Sunday",
        10: "Monday",
        11: "Teusday",
        12: "Wednesday",
        13: "Thursday",
        14: "Friday",
        15: "Saturday",
    }.get(number, "Day that doesnt exist")

class Events(models.Model):
    """
    Events: A database model (object) for Events (Availabiliy).

    Fields:
        event_name: a field that contains the name of a skill
        day: Day of week
        start_time_hour: Hour an event starts (1-24)
        start_time_minute: Minute an event starts (1-60)
        end_time_hour: Hour an event ends (1-24)
        end_time_minute: Minute an event ends (1-60)


    Methods:
        __str__(self):                  Human readeable representation of the Event object.
        save(self, *args, **kwargs):    Overides the default save operator...

        """
    # Day (Is this a character?)
    day = models.CharField(max_length=255,default="")

    # Times stored in 24h format
    # Start time (Hours)
    start_time_hour = models.SmallIntegerField()
    # Start time (Minutes)
    start_time_min = models.SmallIntegerField()
    # End time (Hours)
    end_time_hour = models.SmallIntegerField()
    # End time (Minutes)
    end_time_min = models.SmallIntegerField()
    def __str__(self):
        event_string = "%s -> %02d:%02d - %02d:%02d"%(self.day, self.start_time_hour, self.start_time_min, self.end_time_hour, self.end_time_min)
        #event_string = self.day + "-> " + self.start_time_hour + ":" + self.start_time_min + " - " + self.end_time_hour + ":" + self.end_time_min
        return event_string

    class Meta:
        # Verbose name is the same as class name in this case.
        verbose_name = "Event"
        # Multiple Event objects are referred to as Projects.
        verbose_name_plural = "Events"
        ordering = ('day',)

    def save(self, *args, **kwargs):
        """
        Overides the default save operator...
        Bassically a way to check if the Project object exists in the database. Will be helpful later.
        self.pk is the primary key of the Project object in the database!
        I don't know what super does...
        """
        super(Events, self).save(*args, **kwargs)



class Profile(models.Model):
    """
    Profile: A database model (object) for the user profile.

    Fields:
        user: user object
        bio: bio of user
        known_skills: stores known skills
        interest: stores interest for projects in profile
        isProf: boolean that dictates if the user is a professors

    Methods:
        __str__(self):                  Human readeable representation of the profile object.

    """
    user = models.OneToOneField(User)
    bio = models.TextField(max_length=500, blank=True)
    name = models.TextField(max_length=75, blank=True)
    institution = models.TextField(max_length=100, blank=True)
    location = models.TextField(max_length=100, blank=True)

    # Avail - Availabiliy
    avail = models.ManyToManyField(Events)

    avatar = models.ImageField(upload_to= 'avatars/', default="")

    # TODO: Interest - ManyToOne, Past Classes,
    known_skills = models.ManyToManyField(Skills, related_name="known", default="")
    learn_skills = models.ManyToManyField(Skills, related_name="learn", default="")
    # interest = models.ForeignKey(Project, on_delete=models.CASCADE)

    isProf = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    def __hash__(self):
        return hash(self.user)
    def __eq__(self, other):
        return (self.user == other.user)
    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self == other)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
