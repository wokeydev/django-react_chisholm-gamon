from django import forms


class CareerApplicationForm(forms.Form):
    job_title = forms.CharField(max_length=255, widget=forms.HiddenInput())
    full_name = forms.CharField(max_length=255)
    email = forms.EmailField()
    contact_number = forms.CharField(max_length=50)
    cover_letter = forms.FileField(required=False)
    resume = forms.FileField(required=False)
    comments = forms.CharField(max_length=5000, widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].widget.attrs['placeholder'] = 'Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['contact_number'].widget.attrs['placeholder'] = 'Phone number'
        self.fields['comments'].widget.attrs['placeholder'] = 'Message'

