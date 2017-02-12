from django.db import models

# Import something from django for user auth

"""
The main models of the core app.

Course: A database model (object) for courses



"""

class 

class Course(models.Model):
	course_name = models.CharField(max_length=30, default="general")
	course_info = models.CharField(max_length=100, default="")
	institution = models.CharField(max_length=100, default="collab")
	term = CharField(max_length=100, default="It's alsways Spring")
	year = models.integer()


	def __str__(self):
		return self.course_name

		do that class meta thing to add attributes

class User(models.Model):
	user_first = models.CharField(max_length=20, default="")
	def __str__(self):
		return self.user_first

class Project(models.Model):
	# all many to many fields first, to easily identify relationships
	course = models.ManyToManyField(Course, related_name="course_id")
	project_owner = models.ManyToManyField(User, related_name="po")
	current_members = models.ManyToManyField(User, related_name="members")
	project_name = models.CharField(max_length=50, default="")
	project_info = models.CharField(max_length=100, default="")
	def __str__(self):
		return self.project_name
