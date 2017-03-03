from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models.signals import post_save
from django.dispatch import receiver

from teamwork.apps.projects.models import *


class Skills(models.Model):
    skill = models.CharField(max_length=255, default="")

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


class Profile(models.Model):
    user = models.OneToOneField(User)
    name = models.TextField(max_length=50, blank=True) 
    bio = models.TextField(max_length=500, blank=True)
    email = models.TextField(max_length=50, blank=True)

    # TODO: Interest - ManyToOne, Past Classes, Bio
    known_skills = models.ManyToManyField(Skills, related_name="known", default="")
    learn_skills = models.ManyToManyField(Skills, related_name="learn", default="")
    # interest = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    isProf = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
