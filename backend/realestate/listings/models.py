"""Data storage and processing for REAXML based listings."""

from __future__ import unicode_literals

import re
import arrow
import datetime
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.gis.db import models as gismodels
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField
from django.template.defaultfilters import slugify
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtailgeowidget.edit_handlers import GeoPanel

from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import (RichTextField, FieldRowPanel, FieldPanel, MultiFieldPanel,
                                         InlinePanel, TabbedInterface, ObjectList)
from wagtail.search import index
from django.core.paginator import Paginator
from seo_page.models import SEOFields
from .settings import DEFAULT_PER_PAGE
from wagtail.snippets.models import register_snippet
from .edit_handlers import ListingChooserPanel
from . import enums


class GisClusterableModel(ClusterableModel, gismodels.Model):
    """
    Identical to ClusterableModel but parent class is from geodjango.
    """
    class Meta:
        abstract = True


class REAXMLBoolean(models.BooleanField):
    """Custom boolean field as REAXML accepts strings of "YES" or "NO" for booleans."""

    def to_python(self, value):
        if value in (True, False):
            # if value is 1 or 0 than it's equal to True or False, but we want
            # to return a true bool for semantic reasons.
            return bool(value)
        if value in ('t', 'True', '1', 'YES', 'yes'):
            return True
        if value in ('f', 'False', '0', 'NO', 'no'):
            return False
        raise ValidationError(
            self.error_messages['invalid'],
            code='invalid',
            params={'value': value},
        )


class REAXMLDateTimeField(models.DateTimeField):
    REAXML_DATETIME_FORMATS = [
        "%Y-%m-%d-%H:%M:%S",
        "%Y-%m-%d-%H:%M"
    ]

    def get_prep_value(self, value):
        if value:
            for fmt in self.REAXML_DATETIME_FORMATS:
                try:
                    value = str(datetime.datetime.strptime(value, fmt))
                except (ValueError, TypeError):
                    continue
        return super(REAXMLDateTimeField, self).get_prep_value(value)


class CurrencyIntegerField(models.IntegerField):

    def get_prep_value(self, value):
        try:
            return super(CurrencyIntegerField, self).get_prep_value(value)
        except ValueError:  # Will be thrown if it contains $ or .
            value = str(value).replace('$', '')
            if '.' in value:
                value = value.split('.', 1)[0]
            return super(CurrencyIntegerField, self).get_prep_value(value)


@register_snippet
class PropertyListing(GisClusterableModel, index.Indexed):

    # Base fields
    agentID = models.CharField("Agent ID", max_length=10, help_text="The Office's Source ID")
    uniqueID = models.CharField("Unique ID", max_length=255, help_text="Unique ID of the listing")
    status = models.CharField(max_length=25, db_index=True, choices=enums.STATUS_CHOICES, default=enums.DEFAULT_STATUS)

    property_class = models.CharField(choices=enums.PROPERTY_CLASS_CHOICES, default=enums.DEFAULT_PROPERTY_CLASS,
                                      max_length=25, db_index=True)
    listing_type = models.CharField(choices=enums.LISTING_TYPE_CHOICES, default=enums.DEFAULT_LISTING_TYPE,
                                    max_length=10, db_index=True)

    meta_panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('agentID'),
                FieldPanel('uniqueID'),
            ], "Meta Details"),
            FieldPanel('status'),
            FieldRowPanel([
                FieldPanel('property_class'),
                FieldPanel('listing_type'),
            ])
        ], "Listing Details")
    ]

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    modTime = REAXMLDateTimeField(blank=True, null=True, default=None)  # The REAXML modified time

    priceView = models.CharField(max_length=255, blank=True, default="", verbose_name='Price Display text')
    address_site = models.CharField("Site", max_length=100, blank=True, default="")
    address_subNumber = models.CharField("Unit Number", max_length=100, blank=True, default="")
    address_lotNumber = models.CharField("Lot Number", max_length=100, blank=True, default="")
    address_streetNumber = models.CharField("Street Number", max_length=100, blank=True, default="")
    address_street = models.CharField("Street Name", max_length=100, blank=True, default="")
    address_suburb = models.CharField("Suburb", max_length=100, blank=True, default="", db_index=True)
    address_suburb_display = REAXMLBoolean("Show Suburb", default=True)
    address_state = models.CharField("State", max_length=100, blank=True, default="")
    address_postcode = models.CharField("Postcode", max_length=100, blank=True, default="", db_index=True)
    address_region = models.CharField("Region", max_length=100, blank=True, default="")
    address_country = models.CharField("Country", max_length=100, blank=True, default="Australia")
    address_display = REAXMLBoolean("Show Address", default=True)
    address_streetview = REAXMLBoolean("Show Street View", default=True)
    # address_latitude = models.DecimalField("Latitude", max_digits=9, decimal_places=6, null=True, default=0.0)
    # address_longitude = models.DecimalField("Longitdue", max_digits=9, decimal_places=6, null=True, default=0.0)
    location = gismodels.PointField(srid=4326, null=True, blank=True)

    municipality = models.CharField(max_length=255, blank=True, default="")
    streetDirectory = models.CharField(max_length=255, blank=True, default="")

    headline = models.CharField(max_length=255)
    description = models.TextField()

    address_panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('address_subNumber'),
                FieldPanel('address_lotNumber'),
            ]),
            FieldPanel('address_streetNumber'),
            FieldPanel('address_street'),
            FieldPanel('address_suburb'),
            FieldRowPanel([
                FieldPanel('address_state'),
                FieldPanel('address_postcode'),
            ]),
            # FieldPanel('address_region'),
            # FieldPanel('address_country'),
            FieldRowPanel([
                FieldPanel('address_display'),
                FieldPanel('address_suburb_display'),
                FieldPanel('address_streetview'),
            ]),
            GeoPanel('location')
            # FieldRowPanel([
            #     FieldPanel('address_latitude'),
            #     FieldPanel('address_longitude'),
            # ]),
            # FieldPanel('address_site'),

        ], "Address Details")
    ]

    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(default=0)
    parking = models.IntegerField(default=0)

    description_panels = [
        MultiFieldPanel([
            FieldPanel('headline'),
            FieldPanel('description'),
        ], "Ad Details"),
        FieldPanel('bedrooms'),
        FieldPanel('bathrooms'),
        FieldPanel('parking'),
        InlinePanel('categories', label="Category")
    ]

    buildingDetails_area = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True, default=None)
    buildingDetails_area_unit = models.CharField(max_length=15, blank=True, default="")
    buildingDetails_area_range_min = models.DecimalField(decimal_places=2, max_digits=10,
                                                         blank=True, null=True, default=None)
    buildingDetails_area_range_max = models.DecimalField(decimal_places=2, max_digits=10,
                                                         blank=True, null=True, default=None)
    buildingDetails_energyRating = models.DecimalField(decimal_places=2, max_digits=10,
                                                       blank=True, null=True, default=None)
    buildingDetails_newlyBuilt = REAXMLBoolean(default=False)

    # Sale fields
    price = models.IntegerField(blank=True, null=True, default=0, db_index=True,
                                help_text='The price (number), used for searching')
    price_range_min = models.IntegerField(blank=True, default=0, verbose_name='Search price from')
    price_range_max = models.IntegerField(blank=True, default=0, verbose_name='Search price to')
    price_display = REAXMLBoolean(default=True)
    salebySetDate = REAXMLDateTimeField(blank=True, null=True, default=None, verbose_name="Sale by set date")
    setSale_date = REAXMLDateTimeField(blank=True, null=True, default=None)

    price_panels = [
        MultiFieldPanel([
            FieldPanel('priceView'),
            FieldPanel('price'),
            FieldRowPanel([
                FieldPanel('price_range_min'),
                FieldPanel('price_range_max'),
            ]),
            FieldPanel('price_display'),
            FieldPanel('salebySetDate'),
        ], "Price Details", classname="collapsible collapsed")
    ]

    # TODO: Accomodate soldPrice and soldDate in REAXML instead of price/date
    soldDetails_price = models.IntegerField(blank=True, null=True, default=None)
    soldDetails_price_display = REAXMLBoolean(default=True)
    soldDetails_date = REAXMLDateTimeField(blank=True, null=True, default=None)

    sold_panels = [
        MultiFieldPanel([
            FieldPanel('soldDetails_price'),
            FieldPanel('soldDetails_date'),
            FieldPanel('soldDetails_price_display'),
        ], "Sold Details", classname="collapsible collapsed")
    ]

    underOffer = REAXMLBoolean(default=False, verbose_name='Under Offer?')
    authority = models.CharField(max_length=15, default=enums.DEFAULT_AUTHORITY, choices=enums.AUTHORITY_CHOICES)
    authority_date = REAXMLDateTimeField(blank=True, null=True, default=None)
    auction_date = REAXMLDateTimeField(blank=True, null=True, default=None)

    status_panels = [
        MultiFieldPanel([
            FieldPanel('auction_date'),
            FieldPanel('underOffer'),
            FieldPanel('authority'),
        ], "Sale Details", classname="collapsible collapsed")

    ]

    # Rent Fields
    rent = models.IntegerField(db_index=True, blank=True, null=True, default=None)
    rent_period = models.CharField(max_length=10, choices=enums.RENT_PERIOD_CHOICES,
                                   default=enums.DEFAULT_RENT_PERIOD, blank=True, null=True)
    rent_display = REAXMLBoolean(default=True)
    bond = CurrencyIntegerField(blank=True, null=True, default=None)
    dateAvailable = REAXMLDateTimeField(blank=True, null=True, default=None)

    rent_panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('rent'),
                FieldPanel('rent_period'),
            ]),
            FieldPanel('rent_display'),
            FieldRowPanel([
                FieldPanel('dateAvailable'),
                FieldPanel('bond')
            ])
        ], "Rent Details", classname="collapsible collapsed")
    ]

    # Residential only fields
    isHomeLandPackage = REAXMLBoolean(default=False, verbose_name='Home & Land Package')
    newConstruction = REAXMLBoolean(default=False, verbose_name='New Construction')
    project_id = models.CharField(max_length=50, blank=True, default="")

    # Project/Land features
    estate_name = models.CharField(max_length=255, blank=True, default="")
    estate_stage = models.CharField(max_length=255, blank=True, default="")

    project_panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('isHomeLandPackage'),
                FieldPanel('newConstruction'),
            ]),
            FieldPanel('project_id'),
            FieldPanel('estate_name'),
            FieldPanel('estate_stage'),
        ], "Development Details", classname="collapsible collapsed")
    ]

    # Commercial only features
    commercialAuthority_value = models.CharField(max_length=10, choices=enums.COMMERCIAL_AUTHORITY_CHOICES,
                                                 null=True, blank=True, default=enums.DEFAULT_COMMERCIAL_AUTHORITY,
                                                 verbose_name='Commercial Authority')
    exclusivity_value = models.CharField(max_length=10, choices=enums.COMMERCIAL_EXCLUSIVITY_CHOICES,
                                         null=True, blank=True, default=enums.DEFAULT_COMMERCIAL_EXCLUSIVITY,
                                         verbose_name='Exclusivity')

    commercialRent = models.IntegerField(default=0, help_text='Annually')
    commercialRent_period = "annual"  # Fixed as per DTD
    commercialRent_plusOutgoings = REAXMLBoolean(default=False)
    commercialRent_tax = models.CharField(max_length=10, choices=enums.TAX_CHOICES, default=enums.DEFAULT_TAX)

    outgoings = models.IntegerField(default=0, help_text='Annual outgoings')
    outgoings_period = "annual"  # Fixed as per DTD
    _return = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True,
                                  default=None, help_text='% return annually')
    _return_period = "annual"  # Fixed as per DTD
    _return_unit = "percent"  # Fixed as per DTD

    currentLeaseEndDate = models.DateField(null=True, blank=True, default=None)
    tenancy = models.CharField(max_length=10, choices=enums.TENANCY_CHOICES, default=enums.DEFAULT_TENANCY)
    furtherOptions = models.TextField(blank=True, default="")
    isMultiple = REAXMLBoolean(default=False)

    propertyExtent = models.CharField(max_length=10, blank=True, choices=enums.EXTENT_CHOICES, default="")
    carSpaces = models.IntegerField(default=0)
    parkingComments = models.CharField(max_length=255, blank=True, default="")
    zone = models.CharField(max_length=255, blank=True, default="")

    commercial_panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('commercialAuthority_value'),
                FieldPanel('exclusivity_value'),
            ]),
            FieldPanel('commercialRent'),
            FieldRowPanel([
                FieldPanel('commercialRent_plusOutgoings'),
                FieldPanel('commercialRent_tax'),
            ]),
            FieldPanel('outgoings'),
            FieldPanel('_return'),
            FieldRowPanel([
                FieldPanel('tenancy'),
                FieldPanel('currentLeaseEndDate'),
            ]),
            FieldPanel('furtherOptions'),
            FieldPanel('isMultiple'),
            FieldPanel('propertyExtent'),
            FieldPanel('zone'),
            FieldPanel('carSpaces'),
            FieldPanel('parkingComments')
        ], "Commercial Property Details", classname="collapsible collapsed")
    ]

    # Area details
    area = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True, default=None)
    area_unit = models.CharField(max_length=15, blank=True, default="")
    area_range_min = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True, default=None)
    area_range_max = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True, default=None)
    frontage = models.CharField(max_length=255, blank=True, default="")
    frontage_unit = models.CharField(max_length=15, blank=True, default="")
    depth = models.CharField(max_length=255, blank=True, default="")
    depth_unit = models.CharField(max_length=15, blank=True, default="")
    depth_side = models.CharField(max_length=10, blank=True, default="")
    crossOver_value = models.CharField(max_length=10, blank=True, default="")

    area_panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('area'),
                FieldPanel('area_unit'),
            ]),
            FieldRowPanel([
                FieldPanel('area_range_min'),
                FieldPanel('area_range_max'),
            ]),
            FieldRowPanel([
                FieldPanel('frontage'),
                FieldPanel('frontage_unit'),
            ]),
            FieldRowPanel([
                FieldPanel('depth'),
                FieldPanel('depth_unit'),
                FieldPanel('depth_side'),
            ]),
            FieldPanel('crossOver_value')
        ], "Area Details", classname="collapsible collapsed")
    ]

    extraFields = JSONField(default={}, blank=True)

    media_panels = [
        MultiFieldPanel([
            InlinePanel('images', label="Images"),
            InlinePanel('floorplans', label="Floorplans"),
            InlinePanel('hrefs', label='External Links')
        ], "Media")
    ]

    panels = address_panels + meta_panels + description_panels + price_panels + rent_panels + status_panels + \
        commercial_panels + project_panels + area_panels + media_panels +\
        [
            InlinePanel('agents', label="Agents"),
            InlinePanel('inspections', label="Inpsections"),
            InlinePanel('features', label="Features"),
            FieldPanel('extraFields')
        ]

    search_fields = [
        index.SearchField('address_display_string'),
        index.SearchField('category'),
        index.SearchField('headline'),
        index.SearchField('description'),
        index.SearchField('uniqueID'),
        index.SearchField('address_suburb', boost=5, partial_match=True, es_extra={'analyzer': 'ngram_analyzer'}),
        index.SearchField('address_street', boost=1, partial_match=True),
        index.SearchField('address_state'),
        index.SearchField('address_postcode'),
        index.SearchField('address_region'),
        index.SearchField('address_country'),
        index.FilterField('property_class'),
        index.FilterField('listing_type'),
        index.FilterField('price'),
        index.FilterField('rent'),
        index.FilterField('bedrooms'),
        index.FilterField('bathrooms'),
        index.FilterField('parking'),
        index.FilterField('status'),

    ]

    class Meta:
        unique_together = [('agentID', 'uniqueID')]

    @property
    def category(self):
        try:
            return self.categories.first().name
        except Exception:
            return ""

    def address_display_string(self, override_hide=False):
        address = ""
        if self.address_display is False and not override_hide:
            return "%s, %s %s" % (self.address_suburb, self.address_postcode, self.address_state)

        if self.address_lotNumber:
            address += "Lot: %s " % self.address_lotNumber
        if self.address_subNumber:
            address += self.address_subNumber + "/"
        if self.address_streetNumber:
            address += self.address_streetNumber + " "
        if self.address_street:
            address += self.address_street + " "
        if self.address_suburb and (self.address_suburb_display or override_hide):
            address += self.address_suburb + ", "
        if self.address_state:
            address += self.address_state + " "
        if self.address_postcode:
            address += self.address_postcode
        return address.strip()

    @property
    def address_full(self):
        return self.address_display_string(override_hide=True)

    @classmethod
    def latest_sales(cls):
        return cls.objects.filter(
            status=enums.STATUS_CURRENT,
            listing_type=enums.LISTING_TYPE_SALE
        ).order_by('-created')

    @classmethod
    def latest_rentals(cls):
        return cls.objects.filter(
            status=enums.STATUS_CURRENT,
            listing_type=enums.LISTING_TYPE_LEASE
        ).order_by('-created')

    @classmethod
    def latest_commercial(cls):
        return cls.objects.filter(
            status=enums.STATUS_CURRENT,
            property_class=enums.PROPERTY_CLASS_COMMERCIAL
        ).order_by('-created')

    @classmethod
    def recent_sales(cls):
        return cls.objects.filter(
            status=enums.STATUS_SOLD
        ).order_by('-soldDetails_price')

    @property
    def image(self):
        img = self.images.first()
        return img.image if img else None

    @property
    def agent(self):
        agent = self.agents.first()
        return agent.agent if agent else None

    @property
    def video_urls(self):
        return self.hrefs.all().filter(link_type=enums.LINK_TYPE_VIDEO)

    def __unicode__(self):
        return self.address_full

    def __str__(self):
        return self.address_full

    def get_absolute_url(self):
        return reverse(
            "listing_details", kwargs={
                'slug': slugify(self.address_display_string()),
                'pk': self.pk
            }
        )

    def save(self, *args, **kwargs):
        # We are forcing the suburb to be uppercase for searching
        if self.address_suburb:
            self.address_suburb = self.address_suburb.upper()
        super().save(*args, **kwargs)


class PropertyCategory(Orderable):
    listing = ParentalKey('PropertyListing', related_name='categories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, choices=enums.CATEGORY_CHOICES, db_index=True)


class PropertyFeature(Orderable):
    listing = ParentalKey('PropertyListing', related_name='features', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, db_index=True)
    # As some features are boolean and some values, we will just use int and thuthy
    value = models.IntegerField(default=0)

    panels = [
        FieldRowPanel([
            FieldPanel('name'),
            FieldPanel('value')
        ])
    ]


class ListingAgent(Orderable):
    """The listing agent connection."""
    listing = ParentalKey('PropertyListing', related_name='agents', on_delete=models.CASCADE)
    agent = models.ForeignKey('agents.AgentPage', related_name='listing_agent', on_delete=models.CASCADE)

    panels = [
        FieldPanel('agent')
    ]

    class Meta:
        unique_together = [
            ('agent', 'listing')
        ]


class CurrentInspectionManager(models.Manager):
    """Custom model manager to show current inspections."""

    def get_queryset(self):
        qs = super(CurrentInspectionManager, self).get_queryset()
        return qs.filter(inspection_time__gte=datetime.datetime.now())


class Inspection(models.Model):
    """Storage of <inspectionTimes><inspection> REAXML data."""

    listing = ParentalKey('PropertyListing', related_name='inspections', on_delete=models.CASCADE)
    inspection_time = models.DateTimeField(verbose_name='Start')
    inspection_end_time = models.DateTimeField(blank=True, null=True, default=None, verbose_name='End')

    current = CurrentInspectionManager()
    objects = models.Manager()

    panels = [
        FieldRowPanel([
            FieldPanel('inspection_time'),
            FieldPanel('inspection_end_time'),
        ])
    ]

    def split_from_reaxml(self, inspection_string):
        # Only the following format is accepted as valid: DD-MON-_YYYY_hh:mm[am|pm] to hh:mm[am|pm]
        validate_regex = "^(\d{,2})-(\w{3})-(\d{4}) (\d{,2}):(\d{,2})(am|pm|AM|PM) to (\d{,2}):(\d{,2})(am|pm|AM|PM)$"
        if not re.match(validate_regex, inspection_string):
            print('doesnt match regex')
            return
        try:
            start, end = inspection_string.split("to")
            start = start.strip()
            end = end.strip()
        except Exception:
            start = inspection_string
            end = None

        self.inspection_time = arrow.get(start, "DD-MMM-YYYY h:mmA")
        self.inspection_time.replace(tzinfo=timezone.get_current_timezone_name())
        if end:
            end_hour, end_minute = end.split(':')
            try:
                end_ampm = end_minute[-2:]
                if end_ampm.lower() in ['am', 'pm']:
                    end_minute = end_minute[:-2]
                    end_minute = int(end_minute)
                if end_ampm and end_ampm.lower() == "pm" and int(end_hour) != 12:
                    end_hour = int(end_hour) + 12
                else:
                    end_hour = int(end_hour)
            except Exception:
                pass
            self.inspection_end_time = self.inspection_time.replace(
                hour=end_hour, minute=end_minute
            )
            self.inspection_end_time = self.inspection_end_time.format()
        self.inspection_time = self.inspection_time.format()


class ListingLink(Orderable):
    """URL's for various listing sites (microsite, virtual tour etc.)."""

    listing = ParentalKey('PropertyListing', related_name='hrefs', on_delete=models.CASCADE)
    link_type = models.CharField(choices=enums.LINK_TYPE_CHOICES, max_length=255)
    href = models.URLField()


class Vendor(models.Model):
    """Vendor/Seller details."""

    name = models.CharField(max_length=255, blank=True)
    telephone_bh = models.CharField(max_length=50, blank=True)
    telephone_mobile = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        """Unicode output."""
        return self.name

    @classmethod
    def merge_vendor_records(cls, old, new):
        if isinstance(old, cls) and isinstance(new, cls):
            ListingVendor.objects.filter(vendor_id=old.pk).update(vendor_id=new.pk)
            old.delete()
        else:
            raise Exception("old and new must be of type reaxml_listings.Vendor")


class ListingVendor(Orderable):
    """Link a vendor record to a listing."""
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)


class ListingMediaBase(Orderable):
    external_modtime = models.DateTimeField(blank=True, null=True, default=None,
                                            help_text='Modified Date from External System')
    modtime = models.DateTimeField(auto_now=True)
    media_field = None  # So we can generically grab the media field in processors

    class Meta:
        abstract = True


class ListingImage(ListingMediaBase):
    listing = ParentalKey('PropertyListing', related_name='images', on_delete=models.CASCADE)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    media_field = 'image'
    panels = [ImageChooserPanel('image')]


class ListingFloorplan(ListingMediaBase):
    listing = ParentalKey('PropertyListing', related_name='floorplans', on_delete=models.CASCADE)
    floorplan = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    media_field = 'floorplan'


# Wagtail Page models
class SearchPageFeaturedListing(Orderable):
    page = ParentalKey('realestate.ListingSearchPage', related_name='featured_listings')
    listing = models.ForeignKey('realestate.PropertyListing', on_delete=models.CASCADE)

    panels = [
        ListingChooserPanel('listing')
    ]


class ListingSearchPage(SEOFields, Page):
    search_params = JSONField(blank=True, default={},
                              help_text="Form parameters to pass the backend. DO NOT EDIT without prior knowledge")
    description = RichTextField(blank=True, default="")
    per_page = DEFAULT_PER_PAGE
    per_page_kwarg = 'per_page'
    page_kwarg = 'page'

    subpage_types = None

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        InlinePanel('featured_listings', label="Featured Listings"),
        FieldPanel('search_params'),
    ]

    def get_form(self, request):
        from .forms import ListingSearchForm
        return ListingSearchForm(**self.get_form_kwargs(request))

    def get_per_page(self):
        return getattr(self, self.per_page_kwarg, DEFAULT_PER_PAGE)

    def get_page_number(self):
        return getattr(self, self.page_kwarg, 1)

    def get_form_kwargs(self, request):
        kwargs = {}
        kwargs['data'] = self.search_params.copy()
        kwargs['data'].update(request.GET.dict().copy())
        return kwargs

    def serve(self, request):
        self.per_page = request.POST.get(self.per_page_kwarg, request.GET.get(self.per_page_kwarg, self.per_page))
        self.page = request.POST.get(self.page_kwarg, request.GET.get(self.page_kwarg, 1))
        return super().serve(request)

    def get_listings(self, request):
        return self.get_form(request).as_search(override_params=self.search_params)

    def get_context(self, request, *args, **kwargs):
        context = super(ListingSearchPage, self).get_context(request, *args, **kwargs)
        context['form'] = self.get_form(request)
        listing_paginator = Paginator(self.get_listings(request), self.get_per_page())
        context['listings'] = listing_paginator.page(self.get_page_number())
        try:
            from realestate.agents.models import AgentPage
            context['agent'] = AgentPage.objects.live().get(pk=context['form'].data.get('agent'))
        except (KeyError, ImportError, AgentPage.DoesNotExist):  # If there's no form data
            pass
        return context


ListingSearchPage.edit_handler = TabbedInterface([
    ObjectList(ListingSearchPage.content_panels, heading='Content'),
    ObjectList(ListingSearchPage.promote_panels, heading='Promote'),
    ObjectList(ListingSearchPage.settings_panels, heading='Settings', classname="settings"),
    ObjectList(ListingSearchPage.seo_panels, heading='SEO'),
])
