from django.db import models

# Create your models here.

class Course(models.Model):
	course_name = models.CharField(max_length=30)

class Project(models.Model):
	project_name = models.CharField(max_length=50)

class User(models.Model):
	user_first = models.CharField(max_length=20)
