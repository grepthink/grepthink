#imports forms
from django import forms
#imports all tables from models
from .models import *

#Choices for term
Term_Choice = (
    ('Winter','Winter'),
    ('Spring', 'Spring'),
    ('Summer','Summer'),
    ('Fall','Fall'),
)

#Creates the course form
class CourseForm(forms.ModelForm):

    #Filters queryset based on conditions
    def __init__(self, uid, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)

        #queryset of users other than current user
        other_users = User.objects.exclude(id=uid)
        #queryset containing users who are not superusers
        exclude_superusers = other_users.exclude(is_superuser=True)
        #Renders slug as HiddenInput
        if 'instance' in kwargs:
            self.fields['slug'].widget = forms.HiddenInput()

        #Hides superusers from 'students' field
        self.fields['students'].queryset = exclude_superusers

    #course name field
    name = forms.CharField(
            #Text input
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            #With length 255
            max_length=255,
            #Field required
            required=True
            )

    #course info field
    info = forms.CharField(
            #Text input
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            #With length 255
            max_length=255,
            #Field Required
            required=True
            )

    #Term field
    term = forms. ChoiceField(
            #Choices from Term_Choice
            choices=Term_Choice,
            #Field Required
            required=True
            )

    #Slug Field
    slug = forms.CharField(
            #Text Input
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            #With Length 20
            max_length=20,
            #Field NOT Required
            required=False
            )

    #Students field
    students = forms.ModelMultipleChoiceField(
            #Multiple Choice Selection
            widget=forms.CheckboxSelectMultiple,
            #From all user objects
            queryset=User.objects.all(),
            #Field NOT Required
            required=False
            )

    #Field for only professor creating courses
    limit_creation = forms.BooleanField(
            #Initially field is true
            initial = True,
            #Labeled as "Only professor can create projects?"
            label = 'Only Professor can create projects?',
            #Field NOT Required
            required = False
            )

    #META CLASS
    class Meta:
        model = Course
        fields = ['name','info','term','students','slug']

#Creates join course form
class JoinCourseForm(forms.ModelForm):

    #Initializes form
    def __init__(self, uid, *args, **kwargs):
        super(JoinCourseForm, self).__init__(*args, **kwargs)

    #Add code field
    code = forms.CharField(
            #Text input
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            #With max length 255
            max_length=255
            )

    #META CLASS
    class Meta:
        model = Course
        fields = ['code']

class ShowInterestForm(forms.ModelForm):
    #Initializes form
    def __init__(self, uid, *args, **kwargs):
        slug = kwargs.pop('slug')
        super(ShowInterestForm, self).__init__(*args, **kwargs)

        cur_course = Course.objects.get(slug=slug)
        projects = Project.objects.filter(course=cur_course)
        self.fields['projects'].queryset = projects

    projects = forms.ModelChoiceField(widget=forms.RadioSelect,queryset=Project.objects.all(),required=True,initial=False)

    class Meta:
        model = Course
        fields = ['projects']
