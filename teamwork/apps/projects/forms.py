"""
Teamwork: forms for projects app

Used when creating/editing/deleting projects, adding project updates, and showing intrest in a project.
"""

# Django modules
from django import forms
from django.db.models import *
from django.core.validators import *

from teamwork.apps.courses.models import *
from teamwork.apps.profiles.models import *
from django.core.exceptions import ValidationError
from django.forms import URLField

from .models import *

Lower_Boundary_Choice = ((0, 'No Preference'), (2, '01:00'), (4, '02:00'), (6, '03:00'),
                   (8, '04:00'), (10, '05:00'), (12, '06:00'), (14, '07:00'),
                   (16, '08:00'), (18, '09:00'), (20, '10:00'), (22, '11:00'),
                   (24, '12:00'), )

Upper_Boundary_Choice = ((48, 'No Preference'), (26, '13:00'), (28, '14:00'), (30, '15:00'),
                   (32, '16:00'), (34, '17:00'), (36, '18:00'), (38, '19:00'),
                   (40, '20:00'), (42, '21:00'), (44, '22:00'), (46, '23:00'), )

def ForbiddenNamesValidator(value):
    forbidden_names = ['create', 'all']

    if value.lower() in forbidden_names:
        raise ValidationError('This is a reserved word.')

class CreateProjectForm(forms.ModelForm):
    """
    ModelForm instance used to create/edit/delete a project

    Attributes (Fields):
        title:   [CharField] Name of project
        members:  [Checkbox] Selects project member(s) to create membership object(s)
        accepting: [Boolean] True when project is looking for new teammembers. False when project full.
        sponsor:   [Boolean] True when project is sponsored. False when project created by student.
        course: [Course Obj] Course associated with this project.
        content: [CharField] Verbose project description with markdown support.
        slug:    [CharField] Human readable URL slug

    Methods:
        __init__ :
    """

    # used for filtering the queryset
    def __init__(self, uid, *args, **kwargs):
        super(CreateProjectForm, self).__init__(*args, **kwargs)

        # exclude the superuser

        # identify current user
        user = User.objects.get(id=uid)

        # get_user_enrol
        user_courses = Enrollment.objects.filter(user=user)

        # get_sueruser_list
        superuser = User.objects.filter(is_superuser=True)

        # get_postable_courses
        # Query for a list of courses that the user can post a project in.
        #   limit_creation will be false if the professor allows students to post.
        postable_courses = Course.objects.filter(
            enrollment__in=user_courses).filter(limit_creation=False)

        # get courses created by current user
        created_courses = Course.objects.filter(creator=user)

        # Query for only students, without superuser or professors
        # We use Profile because isProf is stored in the Profile model.
        # TODO: only students in this course
        # only_students = Profile.objects.exclude(
        #     Q(user__in=superuser) | Q(isProf=True) | Q(id=uid))

        # If user is professor
        if user.profile.isProf:
            # can post projects to any course they created
            self.fields['course'].queryset = created_courses
        else:
            # else can only post to any course enrolled in where limit_creation = false
            self.fields['course'].queryset = postable_courses

        # Do not display Sponsor field if user is not a professor
        # Model Profile, isProf set on user creation
        if not user.profile.isProf:
            self.fields['sponsor'].widget = forms.HiddenInput()

        self.fields['title'].validators.append(ForbiddenNamesValidator)

    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=255)

    tagline = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=38)

    accepting = forms.BooleanField(
        initial=True, label='accepting members', required=False)

    sponsor = forms.BooleanField(
        initial=False, label='Sponsored?', required=False)

    desired_skills = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255,
        required=False)

    course = forms.ModelChoiceField(
        widget=forms.RadioSelect,
        queryset=Course.objects.all(),
        required=True,
        initial=False)

    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}), max_length=4000)

    slug = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=20,
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

    teamSize = forms.IntegerField(
        min_value=0, max_value=10, label="Max Team Size",
        required=False)

    lower_time_bound = forms.ChoiceField(
            label="Custom Lower Time Boundary for Scheduling",
            #Choices from Lower_Boundary_Choice
            choices=Lower_Boundary_Choice,
            #Field Required
            required=False)
    upper_time_bound = forms.ChoiceField(
            label="Custom Upper Time Boundary for Scheduling",
            #Choices from Upper_Boundary_Choice
            choices=Upper_Boundary_Choice,
            #Field Required
            required=False)


    class Meta:
        model = Project
        fields = [
            'title', 'tagline', 'accepting', 'sponsor',
            'desired_skills', 'course', 'content', 'slug',
            'weigh_interest', 'weigh_know', 'weigh_learn', 'teamSize',
        ]



class EditProjectForm(forms.ModelForm):
    """
    ModelForm instance used to create/edit/delete a project

    Attributes (Fields):
        title:   [CharField] Name of project
        members:  [Checkbox] Selects project member(s) to create membership object(s)
        accepting: [Boolean] True when project is looking for new teammembers. False when project full.
        sponsor:   [Boolean] True when project is sponsored. False when project created by student.
        course: [Course Obj] Course associated with this project.
        content: [CharField] Verbose project description with markdown support.
        slug:    [CharField] Human readable URL slug

    Methods:
        __init__ :
    """

    # used for filtering the queryset
    def __init__(self, uid, *args, **kwargs):
        super(EditProjectForm, self).__init__(*args, **kwargs)

        # A user cannot edit the slug field after creation,
        #  because it would change the URL associated with the project.
        # 'instance' in kwargs if there exists a project_id matching given slug.
        self.fields['slug'].widget = forms.HiddenInput()

        if 'instance' in kwargs and kwargs['instance']:
            self.fields['accepting'].initial = kwargs['instance'].avail_mem
            self.fields['sponsor'].initial = kwargs['instance'].sponsor

        # Identify current form user
        user = User.objects.get(id=uid)
        # Do not display Sponsor field if user is not a professor
        # Model Profile, isProf set on user creation
        if not user.profile.isProf:
            self.fields['sponsor'].widget = forms.HiddenInput()

    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=255)

    tagline = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=38)

    accepting = forms.BooleanField(label='accepting members', required=False)

    sponsor = forms.BooleanField(label='Sponsored?', required=False)

    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}), max_length=4000)

    slug = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=20,
        required=False)

    teamSize = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True)

    weigh_interest = forms.IntegerField(
        min_value=0, max_value=5, label="Weight of user interest in project",
        required=False)

    weigh_know = forms.IntegerField(
        min_value=0, max_value=5, label="Weight of skills users already know",
        required=False)

    weigh_learn = forms.IntegerField(
        min_value=0, max_value=5, label="Weight of skills users want to learn",
        required=False)

    teamSize = forms.IntegerField(
        min_value=0, max_value=10, label="Max Team Size",
        required=False)

    lower_time_bound = forms.ChoiceField(
            label="Custom Lower Time Boundary for Scheduling",
            #Choices from Lower_Boundary_Choice
            choices=Lower_Boundary_Choice,
            #Field Required
            required=False)
    upper_time_bound = forms.ChoiceField(
            label="Custom Upper Time Boundary for Scheduling",
            #Choices from Upper_Boundary_Choice
            choices=Upper_Boundary_Choice,
            #Field Required
            required=False)

    class Meta:
        model = Project
        fields = [
            'title', 'tagline', 'accepting', 'sponsor',
            'content', 'slug','weigh_interest', 'weigh_know',
            'weigh_learn', 'teamSize'
        ]


class ViewProjectForm(forms.ModelForm):
    """
    Is this still used? - andgates

    """

    def __init__(self, *args, **kwargs):
        super(ViewProjectForm, self).__init__(*args, **kwargs)

    interest = forms.IntegerField(required=False)

    class Meta:
        model = Project
        fields = ['interest']


class UpdateForm(forms.ModelForm):
    """
    Form used for submitting project updates


    Attributes (Fields):
        update_title: [CharField] Name of project update
        update:       [CharField] Project update content
        user:		  [User] 	  User object associated with form submitter

    Methods:
        __init__ :	gets the current user when initiating the form

    """

    # used for filtering the queryset
    def __init__(self, uid, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)

        user = User.objects.get(id=uid)

    update_title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255,
        required=True)

    update = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}), max_length=4000)

    class Meta:
        model = Project
        fields = ['update_title', 'update']

class ResourceForm(forms.ModelForm):

    def __init__(self, uid, *args, **kwargs):
        super(ResourceForm, self).__init__(*args, **kwargs)
        self.fields['src_link'].validators.append(URLValidator)
        user = User.objects.get(id=uid)

    src_title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255,
        required=True)
    src_link = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255,
        required=True)

    class Meta:
        model = Project
        fields = ['src_title', 'src_link']

    def clean(self):
        super(ResourceForm, self).clean()
        if not validate_url(self.cleaned_data.get('src_link')):
            self._errors['src_link'] = self.error_class(['Invalid URL'])

        return self.cleaned_data

def validate_url(url):
    url_form_field = URLField()
    try:
        url = url_form_field.clean(url)
    except ValidationError:
        return False
    return True
