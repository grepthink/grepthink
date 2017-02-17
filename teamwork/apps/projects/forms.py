from django import forms

from .models import *

class ProjectForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255)
    members = forms.ModelMultipleChoiceField(queryset=User.objects.all())
    class Meta:
        model = Project
        fields = ['title']

