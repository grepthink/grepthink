from django import forms

from .models import *

class CourseForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255)
    students = forms.ModelMultipleChoiceField(queryset=User.objects.all())
    class Meta:
        model = Course
        fields = ['name']
