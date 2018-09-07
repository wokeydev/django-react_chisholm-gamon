from django import forms
from ..offices.models import OfficePage
from .models import AgentCategory


class AgentSearchForm(forms.Form):
    ORDER_CHOICES = [
        ('', 'Role'),
        ('title', 'Name A-Z'),
        ('-title', 'Name Z-A'),
        ('job_title', 'Position A-Z'),
        ('-job_title', 'Position Z-A'),
        ('-created', 'Newest'),
        ('-modified', 'Last Updated')
    ]
    DEFAULT_ORDER_CHOICE = None

    agent_name = forms.CharField(max_length=255, required=False,
                                 label='Agent Name', help_text='Search by Agent Name')
    office = forms.ModelChoiceField(queryset=OfficePage.objects.live().order_by('title'),
                                    required=False, empty_label='Choose')
    position = forms.ChoiceField(choices=[], required=False, help_text='Choose')
    sort_by = forms.ChoiceField(choices=ORDER_CHOICES, required=False, initial=DEFAULT_ORDER_CHOICE, label='Sort By')

    def __init__(self, *args, **kwargs):
        super(AgentSearchForm, self).__init__(*args, **kwargs)
        current_positions = AgentCategory.objects.all().values_list('category_name', flat=True).distinct()
        self.fields['position'].choices = [("", "Choose")] + [(i, i) for i in current_positions]

    def as_search(self, qs):
        """
        Accepts a base AgentPage queryset and applied filters based on the validated form.
        """

        if qs is None:
            return None
        if not self.is_valid():
            return qs

        if self.cleaned_data.get('agent_name'):
            qs = qs.filter(title__icontains=self.cleaned_data['agent_name'])

        if self.cleaned_data.get('office'):
            qs = qs.filter(offices__office_id=self.cleaned_data['office'])

        if self.cleaned_data.get('position'):
            qs = qs.filter(categories__category__category_name=self.cleaned_data['position'])

        order_by = self.cleaned_data.get('sort_by')
        if order_by:
            qs = qs.order_by(order_by)
        return qs
