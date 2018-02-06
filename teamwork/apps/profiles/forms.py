# Django Imports
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Used in forms
from teamwork.settings import ALLOWED_SIGNUP_DOMAINS

from .models import *


def SignupDomainValidator(value):
    """
    public method that takes a value
    """
    grepthinkers = ['rmonroe@grepthink.com', 'mgates@grepthink.com',
                    'sdougher@grepthink.com', 'kpannell@grepthink.com']

    # Block any @grepthink email
    if 'grepthink' in value and (value not in grepthinkers):
        raise ValidationError('@grepthink is reserved for employees only. Please use a valid email')
    elif '*' not in ALLOWED_SIGNUP_DOMAINS:
        try:
            domain = value[value.index("@"):]
            # GrepThink accounts only
            if domain not in ALLOWED_SIGNUP_DOMAINS:
                raise ValidationError('Invalid domain. Allowed domains on this network: {0}'.format(
                    ','.join(ALLOWED_SIGNUP_DOMAINS)))  # noqa: E501

        except Exception:
            raise ValidationError('Invalid domain. Allowed domains on this network: {0}'.format(
                ','.join(ALLOWED_SIGNUP_DOMAINS)))  # noqa: E501


def ForbiddenUsernamesValidator(value):
    forbidden_usernames = ['admin', 'settings', 'news', 'about', 'help',
                           'signin', 'signup', 'signout', 'terms', 'privacy',
                           'cookie', 'new', 'login', 'logout', 'administrator',
                           'join', 'account', 'username', 'root', 'blog',
                           'user', 'users', 'billing', 'subscribe', 'reviews',
                           'review', 'blog', 'blogs', 'edit', 'mail', 'email',
                           'home', 'job', 'jobs', 'contribute', 'newsletter',
                           'shop', 'profile', 'register', 'auth',
                           'authentication', 'campaign', 'config', 'delete',
                           'remove', 'forum', 'forums', 'download',
                           'downloads', 'contact', 'blogs', 'feed', 'feeds',
                           'faq', 'intranet', 'log', 'registration', 'search',
                           'explore', 'rss', 'support', 'status', 'static',
                           'media', 'setting', 'css', 'js', 'follow',
                           'activity', 'questions', 'articles', 'network',
                           'grepthink', 'gt', 'groupthink', 'alphanumeric'
                                                            'teamwork']

    if value.lower() in forbidden_usernames:
        raise ValidationError('This is a reserved word.')


def InvalidUsernameValidator(value):
    if '@' in value or '+' in value or '-' in value:
        raise ValidationError('Enter a valid username.')
    # Check for Grepthink or past project Association
    elif 'grepthink' in value or 'groupthink' in value or 'teamwork' in value or 'think' in value:
        raise ValidationError('Invalid GrepThink Association')


def UniqueEmailValidator(value):
    if User.objects.filter(email__iexact=value).exists():
        raise ValidationError('User with this Email already exists.')


def UniqueUsernameIgnoreCaseValidator(value):
    if User.objects.filter(username__iexact=value).exists():
        raise ValidationError('User with this Username already exists.')


class SignUpForm(forms.ModelForm):
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True,
        help_text='Enter a valid Email Address',
        max_length=75)

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm your password",
        required=True)

    class Meta:
        model = User
        exclude = ['last_login', 'date_joined']
        fields = ['email', 'password', 'confirm_password', ]

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].validators.append(UniqueEmailValidator)
        self.fields['email'].validators.append(SignupDomainValidator)

    def clean(self):
        super(SignUpForm, self).clean()
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and password != confirm_password:
            self._errors['password'] = self.error_class(
                ['Passwords don\'t match'])
        return self.cleaned_data


class ProfileForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50, required=False)

    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text='Enter a valid Email Address',
        max_length=75,
        required=False)

    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        max_length=500, required=False)

    institution = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50, required=False)

    location = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50, required=False)

    avatar = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].validators.append(UniqueEmailValidator)
        self.fields['email'].validators.append(SignupDomainValidator)
        if kwargs.get('instance') is not None:
            self.fields['email'].widget.attrs.update([('value', kwargs.get('instance').user.email)])
            self.fields['email'].widget.attrs.update([('disabled', 'true')])

    class Meta:
        model = Profile
        fields = ['name', 'email', 'bio', 'institution', 'location']
