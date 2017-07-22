#imports forms
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from datetime import datetime
from django.contrib.admin.widgets import AdminDateWidget

from teamwork.apps.profiles.models import *

from .models import *

#Choices for term
Term_Choice = (('Winter', 'Winter'), ('Spring', 'Spring'), ('Summer', 'Summer'),
               ('Fall', 'Fall'), )

Lower_Boundary_Choice = ((0, 'No Preference'), (2, '01:00'), (4, '02:00'), (6, '03:00'),
                   (8, '04:00'), (10, '05:00'), (12, '06:00'), (14, '07:00'),
                   (16, '08:00'), (18, '09:00'), (20, '10:00'), (22, '11:00'),
                   (24, '12:00'), )

Upper_Boundary_Choice = ((48, 'No Preference'), (26, '13:00'), (28, '14:00'), (30, '15:00'),
                   (32, '16:00'), (34, '17:00'), (36, '18:00'), (38, '19:00'),
                   (40, '20:00'), (42, '21:00'), (44, '22:00'), (46, '23:00'), )

def ForbiddenNamesValidator(value):
    forbidden_names = ['new', 'join', 'delete', 'create']

    if value.lower() in forbidden_names:
        raise ValidationError('This is a reserved word.')

#Creates the course form
class CreateCourseForm(forms.ModelForm):
    """
    Form used for a user to create a course

    Attributes (Fields):
        name: [CharField] Course name field
        info: [CharField] Course information field
        term: [ChoiceField] List of possible terms
        slug: [CharField] Course slug
        students: [ModelMultipleChoiceField] List of students

    Methods:
        __init__ :  Initializes form, filtering querysets for fields
    """

    #Filters queryset based on conditions
    def __init__(self, uid, *args, **kwargs):
        super(CreateCourseForm, self).__init__(*args, **kwargs)

        #Renders slug as HiddenInput
        if 'instance' in kwargs:
            self.fields['slug'].widget = forms.HiddenInput()
            self.fields['term'].widget = forms.HiddenInput()
        else:
            self.fields['students'].widget = forms.HiddenInput()
            self.fields['limit_interest'].widget = forms.HiddenInput()

        self.fields['name'].validators.append(ForbiddenNamesValidator)

    #course name field
    name = forms.CharField(
        #Text input
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        #With length 255
        max_length=255,
        #Field required
        required=True)

    #course info field
    info = forms.CharField(
        #Text input
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        #With length 255
        max_length=255,
        #Field Required
        required=True)

    #Term field
    term = forms.ChoiceField(
        #Choices from Term_Choice
        choices=Term_Choice,
        #Field Required
        required=True)

    #Slug Field
    slug = forms.CharField(
        #Text Input
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        #With Length 20
        max_length=20,
        #Field NOT Required
        required=False)

    #Students field
    students = forms.ModelMultipleChoiceField(
        #Multiple Choice Selection
        widget=forms.CheckboxSelectMultiple,
        #From all user objects
        queryset=User.objects.all(),
        #Field NOT Required
        required=False)

    #Field for only professor creating courses
    limit_creation = forms.BooleanField(
        #Initially field is false
        initial=False,
        #Labeled as "Only professor can create projects?"
        label='Only Professor can create projects?',
        #Field NOT Required
        required=False)

    limit_weights = forms.BooleanField(
        label="Limit projects to only use specified weights for matches",
        required=False)

    weigh_interest = forms.IntegerField(
        min_value=0, max_value=5, label="Weight of user interest in project",
        required=False)

    weigh_know = forms.IntegerField(
        min_value=0, max_value=5, label="Weight of skills users already know",
        required=False)

    weigh_learn = forms.IntegerField(
        min_value=0, max_value=5, label="Weight of skills users want to learn",
        required=False)

    csv_file = forms.FileField(required=False, label="Upload a CSV Roster")

    # lower_time_bound = forms.ChoiceField(
    #         label="Custom Lower Time Boundary for Scheduling",
    #         #Choices from Lower_Boundary_Choice
    #         choices=Lower_Boundary_Choice,
    #         #Field Required
    #         required=False)
    # upper_time_bound = forms.ChoiceField(
    #         label="Custom Upper Time Boundary for Scheduling",
    #         #Choices from Upper_Boundary_Choice
    #         choices=Upper_Boundary_Choice,
    #         #Field Required
    #         required=False)
    limit_interest = forms.BooleanField(
        label="Disable ability for students to show interest in projects",
        required=False)

    csv_file = forms.FileField(required=False, label="Upload a CSV Roster")

    #META CLASS
    class Meta:
        model = Course
        fields = ['name', 'info', 'term', 'students', 'slug', 'limit_creation',
                'weigh_interest', 'weigh_know', 'weigh_learn', 'limit_weights']


#Edit the course form
class EditCourseForm(forms.ModelForm):
    """
    Form used for a user to create a course

    Attributes (Fields):
        name: [CharField] Course name field
        info: [CharField] Course information field
        term: [ChoiceField] List of possible terms
        slug: [CharField] Course slug
        students: [ModelMultipleChoiceField] List of students

    Methods:
        __init__ :  Initializes form, filtering querysets for fields
    """

    #Filters queryset based on conditions
    def __init__(self, uid, slug, *args, **kwargs):
        super(EditCourseForm, self).__init__(*args, **kwargs)

        curr_course = Course.objects.filter(slug=slug)
        students_in_course = Enrollment.objects.filter(course=curr_course)

        #Renders slug as HiddenInput
        if 'instance' in kwargs:
            self.fields['slug'].widget = forms.HiddenInput()
            self.fields['term'].widget = forms.HiddenInput()
        else:
            self.fields['students'].widget = forms.HiddenInput()
            self.fields['limit_interest'].widget = forms.HiddenInput()

        # get_sueruser_list
        superuser = User.objects.filter(is_superuser=True)
        self.fields['students'].queryset = students_in_course
        self.fields['name'].validators.append(ForbiddenNamesValidator)

    #course name field
    name = forms.CharField(
        #Text input
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        #With length 255
        max_length=255,
        #Field required
        required=True)

    #course info field
    info = forms.CharField(
        #Text input
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        #With length 255
        max_length=255,
        #Field Required
        required=True)

    #Term field
    term = forms.ChoiceField(
        #Choices from Term_Choice
        choices=Term_Choice,
        #Field Required
        required=True)

    #Slug Field
    slug = forms.CharField(
        #Text Input
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        #With Length 20
        max_length=20,
        #Field NOT Required
        required=False)

    #Students field
    students = forms.ModelMultipleChoiceField(
        #Multiple Choice Selection
        widget=forms.CheckboxSelectMultiple,
        #From all user objects
        queryset=User.objects.all(),
        #Field NOT Required
        required=False)

    #Field for only professor creating courses
    limit_creation = forms.BooleanField(
        #Initially field is false
        initial=False,
        #Labeled as "Only professor can create projects?"
        label='Only Professor can create projects?',
        #Field NOT Required
        required=False)

    limit_weights = forms.BooleanField(
        label="Limit projects to only use specified weights for matches",
        required=False)

    weigh_interest = forms.IntegerField(
        min_value=0, max_value=5, label="Weight of user interest in project",
        required=False)

    weigh_know = forms.IntegerField(
        min_value=0, max_value=5, label="Weight of skills users already know",
        required=False)

    weigh_learn = forms.IntegerField(
        min_value=0, max_value=5, label="Weight of skills users want to learn",
        required=False)

    csv_file = forms.FileField(required=False, label="Upload a CSV Roster")

    # lower_time_bound = forms.ChoiceField(
    #         label="Custom Lower Time Boundary for Scheduling",
    #         #Choices from Lower_Boundary_Choice
    #         choices=Lower_Boundary_Choice,
    #         #Field Required
    #         required=False)
    # upper_time_bound = forms.ChoiceField(
    #         label="Custom Upper Time Boundary for Scheduling",
    #         #Choices from Upper_Boundary_Choice
    #         choices=Upper_Boundary_Choice,
    #         #Field Required
    #         required=False)
    limit_interest = forms.BooleanField(
        label="Disable ability for students to show interest in projects",
        required=False)

    csv_file = forms.FileField(required=False, label="Upload a CSV Roster")

    #META CLASS
    class Meta:
        model = Course
        fields = ['name', 'info', 'term', 'students', 'slug', 'limit_creation',
                'weigh_interest', 'weigh_know', 'weigh_learn', 'limit_weights']


#Creates join course form
class JoinCourseForm(forms.ModelForm):
    """
    Form used for a user to join a course

    Attributes (Fields):
        code: [CharField] field for user to enter addcode

    Methods:
        __init__ :  Initializes form
    """

    #Initializes form
    def __init__(self, uid, *args, **kwargs):
        super(JoinCourseForm, self).__init__(*args, **kwargs)

    #Add code field
    code = forms.CharField(
        #Text input
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        #With max length 255
        max_length=255)

    #META CLASS
    class Meta:
        model = Course
        fields = ['code']


def UniqueProjectValidator(value):
    if True:
        raise ValidationError('Each choice must be a Unique Project.')


# Show Interest Form
class ShowInterestForm(forms.ModelForm):
    """
    Form used for showing interest in sepcific projects

    Attributes (Fields):
        projects-5: [ModelChoiceField] Project model
        pxr, x 1:5: [CharField]  Reason for interest in project

    Methods:
        __init__ :  gets the current course when initiating form, sets querysets
        clean:      custom clean method for form validation
    """

    #Initializes form
    def __init__(self, uid, *args, **kwargs):
        slug = kwargs.pop('slug')
        super(ShowInterestForm, self).__init__(*args, **kwargs)

        # Gets course with certain slug
        cur_course = Course.objects.get(slug=slug)

        # Gets all projects in that course
        projects = cur_course.projects.all()

        self.fields['projects'].queryset = projects
        self.fields['projects2'].queryset = projects
        self.fields['projects3'].queryset = projects
        self.fields['projects4'].queryset = projects
        self.fields['projects5'].queryset = projects

        # Hides fields based on # projects in course
        if len(projects) < 5:
            self.fields['projects5'].widget = forms.HiddenInput()
            self.fields['p5r'].widget = forms.HiddenInput()
            if len(projects) < 4:
                self.fields['projects4'].widget = forms.HiddenInput()
                self.fields['p4r'].widget = forms.HiddenInput()
                if len(projects) < 3:
                    self.fields['projects3'].widget = forms.HiddenInput()
                    self.fields['p3r'].widget = forms.HiddenInput()
                    if len(projects) < 2:
                        self.fields['projects2'].widget = forms.HiddenInput()
                        self.fields['p2r'].widget = forms.HiddenInput()
                        if len(projects) < 1:
                            self.fields['projects'].widget = forms.HiddenInput()
                            self.fields['p1r'].widget = forms.HiddenInput()

    #Project Choice Field
    projects = forms.ModelChoiceField(
        queryset=None, empty_label=None, label='First Choice', required=False)
    p1r = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100,
        label='Reason',
        required=False)
    projects2 = forms.ModelChoiceField(
        queryset=None, empty_label=None, label='Second Choice', required=False)
    p2r = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100,
        label='Reason',
        required=False)
    projects3 = forms.ModelChoiceField(
        queryset=None, empty_label=None, label='Third Choice', required=False)
    p3r = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100,
        label='Reason',
        required=False)
    projects4 = forms.ModelChoiceField(
        queryset=None, empty_label=None, label='Fourth Choice', required=False)
    p4r = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100,
        label='Reason',
        required=False)
    projects5 = forms.ModelChoiceField(
        queryset=None, empty_label=None, label='Fifth Choice', required=False)
    p5r = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100,
        label='Reason',
        required=False)

    # Meta class
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


class CourseUpdateForm(forms.ModelForm):
    """
    Form used for submitting project updates

    Attributes (Fields):
        update_title: [CharField] Name of project update
        update:       [CharField] Project update content
        user:         [User]      User object associated with form submitter

    Methods:
        __init__ :  gets the current user when initiating the form
    """

    # used for filtering the queryset
    def __init__(self, uid, *args, **kwargs):
        super(CourseUpdateForm, self).__init__(*args, **kwargs)
        creator = User.objects.get(id=uid)

    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255,
        required=True)

    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}), max_length=2000)

    class Meta:
        model = CourseUpdate
        fields = ['title', 'content']
class AssignmentForm(forms.ModelForm):
    """
    Form used for making a new assignment
    """
    def __init__(self, uid, *args, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)
        creator = User.objects.get(id=uid)

    ass_date = forms.widgets.DateInput()
    due_date = forms.widgets.DateInput()
    ass_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255,
        required=True)

    choices=[('tsr','tsr'),('asg1','asg1'),('asg2','asg2')]

    ass_type = forms.ChoiceField(choices=choices, widget=forms.RadioSelect(), required=True)

    class Meta:
        model= Assignment
        fields = ['ass_date', 'due_date','ass_name','ass_type']
