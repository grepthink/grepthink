from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from teamwork.apps.projects.models import *
# profiles is already imported from projects, not necessary here

def POMatch(project):
	match = {}
	print("\n\nMatching Begun\n\n")
	desired_skills = project.desired_skills.all()
	for i in desired_skills:
		print(i)
		know = i.known.all()
		print("\n\nKnow the Skill")
		print(know)
		for j in know:
			if j.user in match:
				temp = match[j.user]
				temp += 2
				match[j.user] = temp
				print("Updated user score")
			else:
				match[j.user] = 2
				print("Created user score")
			print(j.user)


		# learn = i.learn.all()
		# print("\n\nWant to learn")
		# print(learn)
		
	print("\n\nMatching End\n\n")
	print(match)
	print(len(match.keys()))
	print("\n\n")



# We need to update the User class to use django.auth
# from django.contrib.auth.models import User

# Model definitions for the core app.
# As we move forward, the core app will likely disapear. It's mainly for testing everything out right now.



# Legacy code for me to sort through next and slowly add back in:

"""
#Course: A database model (object) for courses
class Course(models.Model):
	course_name = models.CharField(max_length=30, default="general")
	course_info = models.CharField(max_length=100, default="")
	# Not tested
	institution = models.CharField(max_length=100, default="collab")
	term = models.CharField(max_length=100, default="It's alsways Spring")
	#year = models.DateTime()


	def __str__(self):
		return self.course_name

class User(models.Model):
	user_first = models.CharField(max_length=20, default="")
	def __str__(self):
		return self.user_first

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
