from teamwork.apps.core.models import *
from teamwork.apps.profiles.models import *


class Task(models.Model):
    title = models.CharField(
        max_length=255,
        default="No Title Provided")

    description = models.TextField(
        max_length=255,
        default="")


class ScrumBoard(models.Model):
    title = models.CharField(
        max_length=255,
        default="No Title Provided")

    project = models.ForeignKey(
        Project,
        related_name='membership',
    )

    scrum_master = models.ForeignKey(
        User,
        related_name='scrum_master',
        on_delete=models.CASCADE)

    tagline = models.TextField(
        max_length=38,
        default="Default Project Tagline")

    members = models.ManyToManyField(
        User,
        related_name='membership',
        through='Membership')

    # TODO create proper relations
    tasks = models.ForeignKey(
        Task,
        field='tasks',
        field_name='task',
    )

    def save(self, *args, **kwargs):
        return

    def delete(self, *args, **kwargs):
        return
