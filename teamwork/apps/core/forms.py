"""Core forms."""
from django import forms

from .models import *


class UploadCSVForm(forms.Form):
    """Upload a csv file form.

    Args:
        forms (forms.Form): a CSVForm
    """
    def __init__(self, *args, **kwargs):
        super(UploadCSVForm, self).__init__(*args, **kwargs)

    csv_file = forms.FileField()
