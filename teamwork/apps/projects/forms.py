from django import forms
from teamwork.apps.courses.models import *
from teamwork.apps.profiles.models import *
from .models import *
from django.db.models import *

class ProjectForm(forms.ModelForm):
	# used for filtering the queryset
	def __init__(self, uid, *args, **kwargs):
		super(ProjectForm, self).__init__(*args, **kwargs)
		# Hide slug field if user is editing project
		if 'instance' in kwargs:
			self.fields['slug'].widget = forms.HiddenInput()
		# exclude the superuser

		user = User.objects.get(id=uid)
		user_courses = Enrollment.objects.filter(user=user)
		superuser = User.objects.filter(is_superuser=True)
		only_students = Profile.objects.exclude(Q(user__in=superuser) | Q(isProf=True))

		self.fields['members'].queryset = only_students
		self.fields['course'].queryset = user_courses

		if not user.profile.isProf:
			self.fields['sponsor'].widget = forms.HiddenInput()

	#tp = User.objects.get(id=uid)
	title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),max_length=255)
	members = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,queryset=User.objects.all(), required=False)
	accepting = forms.BooleanField(initial= True, label = 'accepting members', required = False)
	#if tp.profile.isProf:
	sponsor = forms.BooleanField(initial = False, label = 'Sponsored?', required = False)
	course = forms.ModelChoiceField(widget=forms.RadioSelect, queryset=Enrollment.objects.all(),required=True,initial=False)

	content = forms.CharField(
		widget=forms.Textarea(attrs={'class': 'form-control'}),
		max_length=4000)

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
