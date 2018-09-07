from django import forms
from .models import ListingEnquiry


class PageEnquiryForm(forms.Form):
    HELP_CHOICE_APPRIASAL = 'Property appraisal'
    HELP_CHOICE_BUYING = 'Buying a house'
    HELP_CHOICE_RENTING = 'Renting a house'
    HELP_CHOICE_GENERAL = 'General enquiry'
    HELP_CHOICES = (
        (HELP_CHOICE_APPRIASAL, HELP_CHOICE_APPRIASAL),
        (HELP_CHOICE_BUYING, HELP_CHOICE_BUYING),
        (HELP_CHOICE_RENTING, HELP_CHOICE_RENTING),
        (HELP_CHOICE_GENERAL, HELP_CHOICE_GENERAL),
    )

    name = forms.CharField(max_length=255, required=False)
    email_address = forms.EmailField(max_length=255)
    phone_number = forms.CharField(required=False)
    message = forms.CharField(required=False, widget=forms.Textarea)
    help = forms.ChoiceField(
        choices=HELP_CHOICES,
        label='What can we help with?',
        widget=forms.RadioSelect(),
        required=False
    )


class ListingEnquiryForm(forms.ModelForm):
    class Meta:
        model = ListingEnquiry
        exclude = ("sent_by_user",)
        widgets = {
            'listing': forms.HiddenInput()
        }
