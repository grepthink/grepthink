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
    forbidden_names = ['create', 'all', 'delete']

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
            enrollment__in=user_courses).filter(limit_creation=False).filter(disable=False)

        # get courses created by current user
        created_courses = user.course_creator.filter(disable=False)

        # get all courses for GT postings
        GT_courses = Course.objects.all()

        # Query for only students, without superuser or professors
        # We use Profile because isProf is stored in the Profile model.
        # TODO: only students in this course
        # only_students = Profile.objects.exclude(
        #     Q(user__in=superuser) | Q(isProf=True) | Q(id=uid))

        if user.profile.isGT:
            self.fields['course'].queryset = GT_courses
        # If user is professor
        elif user.profile.isProf:
            # can post projects to any course they created
            self.fields['course'].queryset = created_courses
        else:
            # else can only post to any course enrolled in where limit_creation = false
            self.fields['course'].queryset = postable_courses

        # Do not display Sponsor field if user is not a professor
        # Model Profile, isProf set on user creation
        if user.profile.isGT:
            pass
        elif not user.profile.isProf:
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

    # desired_skills = forms.CharField(
    #     widget=forms.TextInput(attrs={'class': 'form-control'}),
    #     max_length=255,
    #     required=False)

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

    no_request = forms.BooleanField(
        label="Do not allow Request to Join",
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


    class Meta:
        model = Project
        fields = [
            'title', 'tagline', 'accepting', 'sponsor',
            'course', 'content', 'slug',
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
        members = kwargs.pop('members', {})
        super(EditProjectForm, self).__init__(*args, **kwargs)

        # A user cannot edit the slug field after creation,
        #  because it would change the URL associated with the project.
        # 'instance' in kwargs if there exists a project_id matching given slug.
        self.fields['slug'].widget = forms.HiddenInput()
        self.fields['project_image'].validators.append(URLValidator)

        if 'instance' in kwargs and kwargs['instance']:
            self.fields['accepting'].initial = kwargs['instance'].avail_mem
            self.fields['sponsor'].initial = kwargs['instance'].sponsor
            self.fields['no_request'].initial = kwargs['instance'].no_request
            self.fields['scrum_master'].queryset = kwargs['instance'].members.all()
            self.fields['project_owner'].queryset = kwargs['instance'].members.all()
            self.fields['project_owner'].initial = kwargs['instance'].creator
            self.fields['scrum_master'].initial = kwargs['instance'].scrum_master



        # Identify current form user
        user = User.objects.get(id=uid)
        # Do not display Sponsor field if user is not a professor
        # Model Profile, isProf set on user creation
        if user.profile.isGT:
            pass
        elif not user.profile.isProf:
            self.fields['sponsor'].widget = forms.HiddenInput()

    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=255)

    tagline = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=38)

    accepting = forms.BooleanField(label='Accepting Members?', required=False)

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

    no_request = forms.BooleanField(
        label="Do no allow Request to Join",
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

    project_image = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),
    max_length=100,
    required=False,
    help_text="Enter a valid Image URL, Example:https://i.imgur.com/example.jpg")

    # Location of Weekly meeting with TA
    ta_location = forms.CharField(
        label="Location of Weekly Meeting w/ TA",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50,
        required=False)

    # Time of Weekly meeting with TA
    ta_time = forms.CharField(
        label="Time of Weekly Meeting w/ TA",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50,
        required=False)

    # scrum_master and project_owner's queryset is set/overridden in init
    scrum_master = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    project_owner = forms.ModelChoiceField(queryset=User.objects.all(), required=False)

    # # Project's Assigned Teacher Assistant
    # assigned_ta = models.ManyToManyField(
    #     User,
    #     related_name='assigned_ta',
    #     default="")

    class Meta:
        model = Project
        fields = [
            'title', 'tagline', 'accepting', 'sponsor', 'ta_location', 'ta_time',
            'content', 'slug','weigh_interest', 'weigh_know', 'project_image',
            'weigh_learn', 'teamSize', 'scrum_master', 'project_owner'
        ]

    def clean(self):
        super(EditProjectForm, self).clean()
        if not validate_url(self.cleaned_data.get('project_image')):
            self._errors['project_image'] = self.error_class(['Invalid URL'])

        return self.cleaned_data

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
        widget=forms.TextInput(attrs={'class': 'form-control'}), label="Title",
        max_length=255,
        required=True)

    update = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}), max_length=4000)

    class Meta:
        model = ProjectUpdate
        fields = ['update_title', 'update']

class ResourceForm(forms.ModelForm):

    def __init__(self, uid, *args, **kwargs):
        super(ResourceForm, self).__init__(*args, **kwargs)
        self.fields['src_link'].validators.append(URLValidator)
        user = User.objects.get(id=uid)

    src_title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Title",
        max_length=255,
        required=True)
    src_link = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="URL Link",
        max_length=255,
        required=True)

    class Meta:
        model = ResourceUpdate
        fields = ['src_title', 'src_link']

    def clean(self):
        super(ResourceForm, self).clean()
        if not validate_url(self.cleaned_data.get('src_link')):
            self._errors['src_link'] = self.error_class(['Invalid URL'])

        return self.cleaned_data

class ChatForm(forms.ModelForm):

    def __init__(self, uid, slug, *args, **kwargs):
        super(ChatForm, self).__init__(*args, **kwargs)

    content = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=2000,
        required=True)

    class Meta:
        model = ProjectChat
        fields = ['content']

# TSR Form
class TSR(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        members = kwargs.pop('members')
        emails = kwargs.pop('emails')
        scrum_master = kwargs.pop('scrum_master')
        super(TSR, self).__init__(*args, **kwargs)

        if not scrum_master:
            self.fields['tasks_comp'].required = False
            self.fields['perf_assess'].required = False
            self.fields['notes'].required = False
            self.fields['tasks_comp'].widget = forms.HiddenInput()
            self.fields['perf_assess'].widget = forms.HiddenInput()
            self.fields['notes'].widget = forms.HiddenInput()

    perc_contribution = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='% Contribution (Values of 0-99 only!)',
        max_digits=2,
        decimal_places=0,
        required=True)

    pos_fb = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Positive Feedback',
        max_length=255,
        required=True)

    neg_fb = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Improvement Suggestion',
        max_length=255,
        required=True)

    tasks_comp = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Tasks Completed (SCRUM Master only)',
        max_length=255,
        required=True)

    perf_assess = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Performance Assessment: Evidence (SCRUM Master Only)',
        max_length=255,
        required=True)

    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Notes/Comments (SCRUM Master Only)',
        max_length=255,
        required=True)

    class Meta:
        model = Tsr
        fields = ['perc_contribution', 'pos_fb', 'neg_fb']

def validate_url(url):
    url_form_field = URLField()
    try:
        url = url_form_field.clean(url)
    except ValidationError:
        return False
    return True
