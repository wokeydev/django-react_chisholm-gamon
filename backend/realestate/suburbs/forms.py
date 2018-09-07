from django import forms

# We will try/except the suburbs DB (for postcode seach) so it can be disabled
try:
    from suburbs_database.models import SuburbData
except ImportError:
    SuburbData = None


class SuburbSearchForm(forms.Form):
    q = forms.CharField(max_length=255, required=False, help_text="Enter a suburb name or postcode")

    def as_search(self, qs):
        # Accepts a queryset of SuburbPage objects and filters
        if not self.is_valid():
            return qs.none()
        if self.cleaned_data.get('q'):
            qs = qs.search(content=self.cleaned_data['q'])

        if SuburbData:
            # We can get postcodes
            data_suburbs = SuburbData.objects.filter(postcode=self.cleaned_data['q'])
            names = data_suburbs.values_list('name', flat=True)
            qs = qs.filter(title__in=names)
        return qs
