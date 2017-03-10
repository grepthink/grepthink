from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from teamwork.apps.projects.models import *
# profiles is already imported from projects, not necessary here

# send in the current list of 
def trim(match):
	uniques = sorted(set(match.values()))
	revision= {}
	p = 0
	# if len(uniques) > 1:
	# 	match = trim(match, uniques)
	while len(uniques) > 5:
		for k,v in match.items():
			if v != uniques[p]:
				revision[k] = v
		p = p + 1
		uniques = sorted(set(revision.values()))
	return revision

def POMatch(project):
	match = {}
	print("\n\nMatching Begun\n\n")
	desired_skills = project.desired_skills.all()
	for i in desired_skills:
		know = i.known.all()
		for j in know:
			if j.user in match:
				temp = match[j.user]
				temp += 2
				match[j.user] = temp
			else:
				match[j.user] = 2	
		learn = i.learn.all()
		for k in learn:
			if k.user in match:
				temp = match[k.user]
				temp += 1
				match[k.user] = temp
			else:
				match[k.user] = 2
	print(match)
	skillMatches = trim(match)
	print(skillMatches)
	print("\n\nMatching End\n\n")



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
