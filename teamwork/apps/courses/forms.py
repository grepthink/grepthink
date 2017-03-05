from django import forms

from .models import *

# again the multiple choice
Term_Choice = (
    ('Winter','Winter'),
    ('Spring', 'Spring'),
    ('Summer','Summer'),
    ('Fall','Fall'),
)

class CourseForm(forms.ModelForm):

    # used for filtering the queryset
    def __init__(self, uid, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        # exclude the current user and the superuser
        if 'instance' in kwargs:
            self.fields['slug'].widget = forms.HiddenInput()
        self.fields['students'].queryset = User.objects.exclude(id=uid).exclude(is_superuser=True)

    name = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            max_length=255,
            required=True
            )
    info = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            max_length=255, required=True
            )
    term = forms. ChoiceField(choices=Term_Choice,required=True)
    slug = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            max_length=20,
            required=False
            )
    students = forms.ModelMultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,queryset=User.objects.all(),
            required=False
            )
    professor = forms.BooleanField(initial = True, label = 'Only Professor can create projects?', required = False)

    class Meta:
        model = Course
        fields = ['name','info','term','students','slug']


class JoinCourseForm(forms.ModelForm):

    def __init__(self, uid, *args, **kwargs):
        super(JoinCourseForm, self).__init__(*args, **kwargs)

    code = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            max_length=255
            )
    """
    students = forms.ModelMultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,queryset=User.objects.all()
    )
    """
    class Meta:
        model = Course
        fields = ['code']
