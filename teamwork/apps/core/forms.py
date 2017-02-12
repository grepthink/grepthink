from django.forms import ModelForm
from .models import *
from django import forms

class ProjectForm(ModelForm):
    #course_name = forms.CharField(max_length=30)
    class Meta:
        model = Project
        fields = '__all__'
