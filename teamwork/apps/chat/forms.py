"""
Teamwork: forms for chat app

Used when creating/editing/deleting chatrooms.
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

def ForbiddenNamesValidator(value):
    forbidden_names = ['create', 'all', 'delete']

    if value.lower() in forbidden_names:
        raise ValidationError('This is a reserved word.')

class CreateChatForm(forms.ModelForm):

    def __init__(self, uid, *args, **kwargs):
        super(CreateChatForm, self).__init__(*args, **kwargs)

        user_creator = User.objects.get(id=uid)

        name = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=255)

        user = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=75)

    class Meta:
        model = Chatroom
        fields = [
            'name', 'user'
        ]

def validate_url(url):
    url_form_field = URLField()
    try:
        url = url_form_field.clean(url)
    except ValidationError:
        return False
    return True
