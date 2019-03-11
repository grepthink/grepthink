"""
Teamwork: profiles

Database Models for the objects: Skills, Profile
"""

# Django Imports
from __future__ import unicode_literals

# Third-party Modules
import markdown
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import timezone


import google.oauth2.credentials
class Credentials(models.Model):
    user=models.OneToOneField(User)
    access_token=models.TextField(default="")
    refresh_token=models.TextField(default="")
    client_id=models.TextField(default="")
    client_secret=models.TextField(default="")
    scopes=models.TextField(default="")
    invalid=models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    class Meta:
        # Verbose name is the same as class name in this case.
        verbose_name = "Credential"
        # Multiple Skill objects are referred to as Projects.
        verbose_name_plural = "Credentials"
        ordering = ('user',)

    def save(self, *args, **kwargs):   
       super(Credentials, self).save(*args, **kwargs) # Call the real save() method

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
        11: "Tuesday",
        12: "Wednesday",
        13: "Thursday",
        14: "Friday",
        15: "Saturday",
    }.get(number, "Day that doesnt exist")

class Events(models.Model):
    """
    Events: A database model (object) for Events (Availability).

    Fields:
        day: Day of week
        start_time_hour: Hour an event starts (1-24)
        start_time_min: Minute an event starts (1-60)
        end_time_hour: Hour an event ends (1-24)
        end_time_min: Minute an event ends (1-60)


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


class Alert(models.Model):
    """
    Alert: A notification directed to a specific user

    Fields:
        sender  - User: person sending alert, or None (if System)
        to      - User: person receiving alert
        date    - DateTime: time sent
        msg     - str: alert body
        read    - boolean: whether alert has been written/marked as read
        url     - str: URL for related page, or None

    Types:
        'course_inv'    - invitation to a course
    """

    sender = models.ForeignKey(User, default=None, related_name="sender")
    to = models.ForeignKey(User, related_name="to")
    date = models.DateTimeField(auto_now_add=True)
    msg = models.CharField(max_length=500)
    read = models.BooleanField(default=False)
    url = models.CharField(max_length=500,default="")

    # Slug is used to accept invitations
    slug = models.CharField(
        max_length=20,
        default="")

    # two alert types: basic and invitation
    alertType = models.CharField(max_length=30, default="basic")

    def __str__(self):
        return str(self.sender) + " -> " + str(self.to) + " : " + str()

    class Meta:
        # Verbose name is the same as class name in this case.
        verbose_name = "Alert"
        # Multiple Event objects are referred to as Projects.
        verbose_name_plural = "Alerts"
        ordering = ('date',)

    def save(self, *args, **kwargs):
        super(Alert, self).save(*args, **kwargs)


def validate_image(fieldfile_obj):
    filesize = fieldfile_obj.file.size
    megabyte_limit = 5.0
    if filesize > megabyte_limit*1024*1024:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
    else:
        print("file size okay")

class Profile(models.Model):
    """
    Profile: A database model (object) for the user profile.

    Fields:
        user: user object
        bio: bio of user
        known_skills: stores known skills
        interest: stores interest for projects in profile
        isProf: boolean that dictates if the user is a professor
        isTa: boolean that indicates if the user is a teaching assistant

    Methods:
        __str__(self):                  Human readeable representation of the profile object.

    """
    user = models.OneToOneField(User)
    bio = models.TextField(max_length=500, blank=True)
    name = models.TextField(max_length=75, blank=True)
    institution = models.TextField(max_length=100, blank=True)
    location = models.TextField(max_length=100, blank=True)

    # Availability
    avail = models.ManyToManyField(Events)
    jsonavail = models.TextField(
                default='[]')

    # Profile Image
    avatar = models.ImageField(
                upload_to= 'avatars/%Y/%m/%d/',
                validators=[validate_image],
                default="",
                null=True,
                blank=True)

    known_skills = models.ManyToManyField(Skills, related_name="known", default="")
    learn_skills = models.ManyToManyField(Skills, related_name="learn", default="")



    claimed_projects = models.ManyToManyField('projects.Project', related_name="claimed_projects", default="")

    isProf = models.BooleanField(default=False)
    isGT = models.BooleanField(default=False)

    # don't believe this is used anywhere 9/24
    isTa = models.BooleanField(default=False)
    meeting_limit = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        string = "%s (%s)"%(self.user.email, self.name)
        return string
    def __hash__(self):
        return hash(self.user)
    def __eq__(self, other):
        return (self.user == other.user)
    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self == other)

    def get_bio_as_markdown(self):
        return markdown.markdown(self.bio, safe_mode='escape')

    # Alert functions, self explanitory
    def alerts(self):
        return Alert.objects.filter(to=self.user)
    def unread_alerts(self):
        return Alert.objects.filter(to=self.user,read=False)
    def read_alerts(self):
        return Alert.objects.filter(to=self.user,read=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
