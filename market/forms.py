from django import forms
from .models import TRANSACTION_MODES


class StockTransactionForm(forms.Form):
    mode = forms.ChoiceField(choices=TRANSACTION_MODES)
    quantity = forms.CharField(required=True,
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Enter integers only',
                                   'title': 'Enter integers only',
                                   'pattern': '[0-9]+'
                               }))


