from django.contrib.auth.models import User
from django.db import models


class Board(models.Model):
    tittle = models.CharField(max_length=100)
    description = models.CharField(max_length=200)


class Task(models.Model):
    assigned = models.BooleanField(default=False)
    category = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
