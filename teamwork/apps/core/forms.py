from django import forms

from .models import *

"""
Upload a csv file form

"""
class UploadCSVForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UploadCSVForm, self).__init__(*args, **kwargs)

    csv_file = forms.FileField()
