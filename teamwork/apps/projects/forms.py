from django import forms

from .models import *

class ProjectForm(forms.ModelForm):
	# used for filtering the queryset
	def __init__(self, uid, *args, **kwargs):
		super(ProjectForm, self).__init__(*args, **kwargs)
		# exclude the current user and the superuser
		self.fields['members'].queryset = User.objects.exclude(is_superuser=True)

	title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),max_length=255)
	members = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,queryset=User.objects.all(), required=False)
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