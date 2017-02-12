from django.forms import ModelForm
from .models import Course
from django import forms

class CourseForm(ModelForm):
    course_name = forms.CharField(max_length=30)
    class Meta:
        model = Course
        fields = ['course_name', 'course_info']
