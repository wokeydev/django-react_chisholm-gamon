import datetime
from django import forms
from django.db.models import Q, Case, Value, When, IntegerField
from wagtail.search.backends import get_search_backend
from django.contrib.gis.geos import Polygon
from .models import PropertyListing, Inspection
from . import enums

try:
    from realestate.agents.models import AgentPage
except ImportError:
    AgentPage = None

try:
    from suburbs_database.models import SuburbData
except ImportError:
    SuburbData = None


class ListingSearchForm(forms.Form):
    query = forms.CharField(required=False)
    uniqueID = forms.CharField(required=False)
    status = forms.ChoiceField(choices=enums.STATUS_CHOICES, initial=enums.DEFAULT_STATUS, required=False)
    property_class = forms.ChoiceField(choices=enums.PROPERTY_CLASS_CHOICES, required=False, label="Property Type")
    listing_type = forms.ChoiceField(choices=enums.LISTING_TYPE_CHOICES, required=False)
    address_suburb = forms.CharField(required=False)
    surrounding = forms.BooleanField(required=False, initial=True)
    address_state = forms.CharField(required=False)
    bedrooms__gte = forms.IntegerField(required=False, label='Bedrooms')
    bathrooms__gte = forms.IntegerField(required=False, label='Bathrooms')
    parking__gte = forms.IntegerField(required=False, label='Parking')
    price__gte = forms.IntegerField(required=False, label='$ min')
    price__lte = forms.IntegerField(required=False, label='$ max')
    categories = forms.MultipleChoiceField(choices=enums.CATEGORY_CHOICES, required=False)
    order_by = forms.ChoiceField(required=False, choices=enums.ORDER_BY_CHOICES, label='Sort by')
    boundaries = forms.CharField(max_length=1500, required=False)
    area__gte = forms.IntegerField(required=False, label='Land Area')
    buildingDetails_area__gte = forms.IntegerField(required=False, label='Building Area')

    # Boundaries should be provides as "lat lng, lat lng"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if AgentPage:
            self.fields['agent'] = forms.ModelChoiceField(
                queryset=AgentPage.objects.live(),
                required=False
            )

    def as_search(self, override_params={}):
        order_by = override_params.pop('order_by', enums.DEFAULT_ORDER_BY)
        order_by = order_by.split(',')
        override_params = {k: v for k, v in override_params.items() if v}  # Clear out empty strings
        qs = PropertyListing.objects.filter(**override_params)

        if not self.is_valid():
            return qs

        data = self.cleaned_data

        if data.get('address_suburb'):
            suburbs = data.get('address_suburb').split(',')
            try:

                suburbs_q = Q()
                for suburb in suburbs:
                    suburbs_q = suburbs_q | Q(name__iexact=suburb)

                s = SuburbData.objects.filter(suburbs_q)

                if data.get('address_state'):
                    s = s.filter(state_code=data['address_state'])

                if data.get('surrounding'):
                    surrounding_suburb_ids = [
                        item for sublist in s.values_list('bordering_locations', flat=True) for item in sublist
                    ]
                    surrounding_suburbs = SuburbData.objects.filter(
                        pk__in=surrounding_suburb_ids
                    )
                else:
                    surrounding_suburbs = SuburbData.objects.none()

                qs = qs.filter(
                    Q(address_suburb__in=suburbs) |
                    Q(address_suburb__in=[i.upper() for i in surrounding_suburbs.values_list('name', flat=True)])
                )
                # The listings are created with suburb in title case.

                qs = qs.annotate(
                    suburb_first=Case(
                        When(address_suburb__in=suburbs, then=Value(0)),
                        default=Value(1),
                        output_field=IntegerField()
                    )
                )
                if data.get('order_by'):
                    order_by = ['suburb_first'] + data.get('order_by', '').split(',') or order_by

                del(data['address_suburb'])

            except AttributeError:
                pass

        if data.get('agent'):
            qs = qs.filter(agents__agent=data.pop('agent'))

        for field, val in data.items():
            if field == 'categories' and val:
                qs = qs.filter(categories__name__in=val)
            elif hasattr(PropertyListing, field) and val:
                qs = qs.filter(**{field: val})
            elif "__" in field and hasattr(PropertyListing, field.split('__')[0]) and val:
                try:
                    val = val.split(',')
                except Exception:
                    pass
                qs = qs.filter(**{field: val})

        if data.get('boundaries'):
            boundary_pairs = data['boundaries'].split(',')
            if boundary_pairs:
                poly = Polygon(tuple((float(i.split('+')[0]), float(i.split('+')[1])) for i in boundary_pairs))
                qs = qs.filter(location__coveredby=poly)

        if data.get('query'):
            return get_search_backend().search(data['query'], qs, operator="or")
        if data.get('order_by'):
            order_by = data['order_by'].split(',')
        return qs.order_by(*order_by)


class ListingInspectionSearchForm(forms.Form):
    property_class = forms.ChoiceField(choices=enums.PROPERTY_CLASS_CHOICES, required=False)
    listing_type = forms.ChoiceField(choices=enums.LISTING_TYPE_CHOICES, required=False)
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_from'].initial = datetime.date.today()
        self.fields['date_to'].initial = datetime.date.today() + datetime.timedelta(days=7)

    def as_search(self, override_params={}):
        listing_qs = PropertyListing.objects.filter(**override_params)
        inspection_qs = Inspection.current.all()
        if not self.is_valid():
            return inspection_qs

        if self.cleaned_data.get('property_class'):
            listing_qs = listing_qs.filter(property_class=self.cleaned_data['property_class'])
        if self.cleaned_data.get('listing_type'):
            listing_qs = listing_qs.filter(listing_type=self.cleaned_data['listing_type'])

        if self.cleaned_data.get('date_from'):
            inspection_qs = inspection_qs.filter(inspection_time__gte=self.cleaned_data['date_from'])

        if self.cleaned_data.get('date_to'):
            inspection_qs = inspection_qs.filter(inspection_time__lte=self.cleaned_data['date_to'])

        listing_ids = listing_qs.values_list('pk', flat=True)
        listing_ids = list(listing_ids)
        return inspection_qs.filter(listing_id__in=listing_ids).order_by('inspection_time')


class ListingAuctionSearchForm(ListingSearchForm):
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_from'].initial = datetime.date.today()

    def as_search(self, override_params={'status': enums.STATUS_CURRENT}):
        qs = super().as_search(override_params=override_params)
        qs = qs.filter(auction_date__isnull=False)

        # Date from will default to Today unless specified
        if self.cleaned_data.get('date_from'):
            qs = qs.filter(auction_date__gte=self.cleaned_data['date_from'])
        else:
            qs = qs.filter(auction_date__gte=datetime.date.today())

        if self.cleaned_data.get('date_to'):
            qs = qs.filter(auction_date__lte=self.cleaned_data['date_to'])
        if 'order_by' not in override_params:
            qs = qs.order_by('auction_date')
        return qs
