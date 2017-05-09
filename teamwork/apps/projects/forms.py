"""
Teamwork: forms for projects app

Used when creating/editing/deleting projects, adding project updates, and showing intrest in a project.
"""

# Django modules
from django import forms
from django.db.models import *

from teamwork.apps.courses.models import *
from teamwork.apps.profiles.models import *

from .models import *


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

    class Meta:
        model = Project
        fields = [
            'title', 'tagline', 'accepting', 'sponsor',
            'desired_skills', 'course', 'content', 'slug',
            'weigh_interest', 'weigh_know', 'weigh_learn',
        ]



class ProjectForm(forms.ModelForm):
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
        super(ProjectForm, self).__init__(*args, **kwargs)

        # A user cannot edit the slug field after creation,
        #  because it would change the URL associated with the project.
        # 'instance' in kwargs if there exists a project_id matching given slug.
        if 'instance' in kwargs:
            # Hide slug field if user is editing project
            self.fields['slug'].widget = forms.HiddenInput()
        else:
            self.fields['resource'].widget = forms.HiddenInput()

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

        # Prepopulate course
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['course'].initial = next(course for course in
                    self.fields['course'].queryset if kwargs['instance'] in
                    course.projects.all())

        # Do not display Sponsor field if user is not a professor
        # Model Profile, isProf set on user creation
        if not user.profile.isProf:
            self.fields['sponsor'].widget = forms.HiddenInput()

        #mems_in_proj = Membership.objects.filter(project=kwargs['instance'])
        #self.fields['members'].queryset = mems_in_proj

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

    resource = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        max_length=4000,
        required=False)

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

    class Meta:
        model = Project
        fields = [
            'title', 'tagline', 'accepting', 'sponsor',
            'desired_skills', 'course', 'content', 'slug', 'resource',
            'weigh_interest', 'weigh_know', 'weigh_learn'
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
