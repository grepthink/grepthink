from django import forms
from teamwork.apps.courses.models import *
from .models import *

class ProjectForm(forms.ModelForm):
	# used for filtering the queryset
	def __init__(self, uid, *args, **kwargs):
		super(ProjectForm, self).__init__(*args, **kwargs)
		# Hide slug field if user is editing project
		if 'instance' in kwargs:
			self.fields['slug'].widget = forms.HiddenInput()
		# exclude the superuser
		#TODO: exclude professors
		user = User.objects.get(id=uid)
		self.fields['members'].queryset = User.objects.exclude(is_superuser=True)
		self.fields['course'].queryset = Enrollment.objects.filter(user=user)
		if not user.profile.isProf:
			self.fields['sponsor'].widget = forms.HiddenInput()

	#tp = User.objects.get(id=uid)
	title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),max_length=255)
	members = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,queryset=User.objects.all(), required=False)
	accepting = forms.BooleanField(initial= True, label = 'accepting members', required = False)
	#if tp.profile.isProf:
	sponsor = forms.BooleanField(initial = False, label = 'Sponsored?', required = False)
	course = forms.ModelChoiceField(widget=forms.RadioSelect, queryset=Enrollment.objects.all(),required=True,initial=False)

	slug = forms.CharField(
    	widget=forms.TextInput(attrs={'class': 'form-control'}),
    	max_length=20,
    	required=False
    	)
	
	class Meta:
	    model = Project
	    fields = ['title']

class ViewProjectForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(ViewProjectForm, self).__init__(*args, **kwargs)


	interest = forms.IntegerField(required=False)

	class Meta:
	    model = Project
	    fields = ['interest']
