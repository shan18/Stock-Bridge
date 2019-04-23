from django import forms
from .models import TRANSACTION_MODES


class CompanyChangeForm(forms.Form):
    price = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'pattern': '[0-9]+',
        'title': 'Enter integers only',
        'placeholder': 'Enter positive integers only'
    }))
