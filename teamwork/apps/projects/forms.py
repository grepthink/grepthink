"""
Teamwork: forms for projects app

Used when creating/editing/deleting projects, adding project updates, and showing intrest in a project.
"""

# Django modules
from django import forms
from django.db.models import *

# Local modules
 # Import project database models
from .models import *
 # Import course database models
from teamwork.apps.courses.models import *
 # Import profile database models
from teamwork.apps.profiles.models import *

class ProjectForm(forms.ModelForm):
	"""
	ModelForm instance used to create/edit/delete a project

	Attributes (Fields):
		title:   [CharField] Name of project
		members:  [Checkbox] Selects project member(s) to create membership object(s)
		accepting: [Boolean] True when project is looking for new teammembers. False when project full.
		sponsor:   [Boolean] True when project is sponsored. False when project created by student.
		course: [Course Obj] Course associated with this project.
		content: [CharField] Verbose project description with markdown support.
		slug:    [CharField] Human readable URL slug

	Methods:
		__init__ : 
	"""
	# used for filtering the queryset
	def __init__(self, uid, *args, **kwargs):
		super(ProjectForm, self).__init__(*args, **kwargs)
		
		# A user cannot edit the slug field after creation, 
		#  because it would change the URL associated with the project.
		# 'instance' in kwargs if there exists a project_id matching given slug.
		if 'instance' in kwargs:
			# Hide slug field if user is editing project
			self.fields['slug'].widget = forms.HiddenInput()


		# exclude the superuser

		# identify current user
		user = User.objects.get(id=uid)

		# get_user_enrol
		user_courses = Enrollment.objects.filter(user=user)

		# get_sueruser_list
		superuser = User.objects.filter(is_superuser=True)

		# get_user_enrollmentns
		postable_courses = Course.objects.filter(
			enrollment__in=user_courses).filter(limit_creation=False
			)

		only_students = Profile.objects.exclude(
			Q(user__in=superuser) | Q(isProf=True)
			)


		self.fields['members'].queryset = only_students
		self.fields['course'].queryset = postable_courses

		# Do not display Sponsor field if user is not a professor
		# Model Profile, isProf set on user creation
		if not user.profile.isProf:
			self.fields['sponsor'].widget = forms.HiddenInput()

	title = forms.CharField(
		widget=forms.TextInput(attrs={'class': 'form-control'}),
		max_length=255
		)

	members = forms.ModelMultipleChoiceField(
		widget=forms.CheckboxSelectMultiple,
		queryset=User.objects.all(),
		required=False)

	accepting = forms.BooleanField(initial= True,
		label = 'accepting members',
		required = False
		)

	sponsor = forms.BooleanField(initial = False,
		label = 'Sponsored?',
		required = False)

	course = forms.ModelChoiceField(
		widget=forms.RadioSelect,
		queryset=Course.objects.all(),
		required=True,initial=False
		)

	content = forms.CharField(
		widget=forms.Textarea(attrs={'class': 'form-control'}),
		max_length=4000
		)

	slug = forms.CharField(
    	widget=forms.TextInput(attrs={'class': 'form-control'}),
    	max_length=20,
    	required=False
    	)

	class Meta:
	    model = Project
	    fields = ['title', 'members', 'accepting', 'sponsor', 'course', 'content', 'slug']

class ViewProjectForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(ViewProjectForm, self).__init__(*args, **kwargs)


	interest = forms.IntegerField(required=False)

	class Meta:
	    model = Project
	    fields = ['interest']

class UpdateForm(forms.ModelForm):
	# used for filtering the queryset
	def __init__(self, uid, *args, **kwargs):
		super(UpdateForm, self).__init__(*args, **kwargs)

		user = User.objects.get(id=uid)

	update_title = forms.CharField(
    	widget=forms.TextInput(attrs={'class': 'form-control'}),
    	max_length=255,
    	required=True
    	)

	update = forms.CharField(
		widget=forms.Textarea(attrs={'class': 'form-control'}),
		max_length=4000)


	class Meta:
	    model = Project
	    fields = ['update_title', 'update']
