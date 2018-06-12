from django import forms

from .models import *

"""
Upload a csv file form

"""
class UploadCSVForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UploadCSVForm, self).__init__(*args, **kwargs)

    csv_file = forms.FileField()

"Form to handle donations/payments"
class PaymentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)

    amount = forms.DecimalField(
        # Max amount of digits
        max_digits=6,
        # Two decimal places for Currency
        decimal_places=2)

    memo = forms.CharField(
        # Text input
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        # Max length of 255 characters
        max_length=255)
