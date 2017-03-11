#imports forms
from django import forms
#imports all tables from models
from .models import *
from django.core.exceptions import ValidationError

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

def UniqueProjectValidator(value):
    if True:
        raise ValidationError('Each choice must be a Unique Project.')

class ShowInterestForm(forms.ModelForm):
    #Initializes form
    def __init__(self, uid, *args, **kwargs):
        slug = kwargs.pop('slug')
        super(ShowInterestForm, self).__init__(*args, **kwargs)

        cur_course = Course.objects.get(slug=slug)
        #USE THIS SEAN U DUMMY
        projects = cur_course.projects.all()
        self.fields['projects'].queryset = projects
        self.fields['projects2'].queryset = projects
        self.fields['projects3'].queryset = projects
        self.fields['projects4'].queryset = projects
        self.fields['projects5'].queryset = projects


        if len(projects) < 5:
            self.fields['projects5'].widget = forms.HiddenInput()
            if len(projects) < 4:
                self.fields['projects4'].widget = forms.HiddenInput()
                if len(projects) < 3:
                    self.fields['projects3'].widget = forms.HiddenInput()
                    if len(projects) < 2:
                        self.fields['projects2'].widget = forms.HiddenInput()
                        if len(projects) < 1:
                            self.fields['projects'].widget = forms.HiddenInput()
    #projects = forms.ModelChoiceField(widget=forms.RadioSelect,queryset=Project.objects.all(),required=True,initial=False)

    #Project Choice Field
    projects = forms.ModelChoiceField(queryset=None, empty_label=None, label='First Choice', required = False)
    projects2 = forms.ModelChoiceField(queryset=None, empty_label=None, label='Second Choice', required = False)
    projects3 = forms.ModelChoiceField(queryset=None, empty_label=None, label='Third Choice', required = False)
    projects4 = forms.ModelChoiceField(queryset=None, empty_label=None, label='Fourth Choice', required = False)
    projects5 = forms.ModelChoiceField(queryset=None, empty_label=None, label='Fifth Choice', required = False)

    class Meta:

        model = Course

        fields = ['projects']

    # Overrides clean_data for Show_Interest
    def clean(self):
        data = self.cleaned_data

        # Initializes a list of projects
        project_list = []
        # Gets data and adds to list
        p1 = data.get('projects')
        p2 = data.get('projects2')
        p3 = data.get('projects3')
        p4 = data.get('projects4')
        p5 = data.get('projects5')
        project_list.append(p1)
        project_list.append(p2)
        project_list.append(p3)
        project_list.append(p4)
        project_list.append(p5)

        # Filters None from project list for error checking
        project_list = list(filter(None, project_list))

        # Checks for uniqueness
        if len(project_list) != len(set(project_list)):
            self._errors['projects'] = self.error_class(
                ['Choices must be unique!'])
            #raise forms.ValidationError("Choices must be unique.")

        return data
