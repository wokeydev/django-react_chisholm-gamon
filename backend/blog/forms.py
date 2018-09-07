from django import forms


class BlogSearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search')
