import json
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from modelcluster.fields import ParentalKey
from wagtail.core.models import Page, Orderable
from wagtail.admin.edit_handlers import (FieldPanel, RichTextField, TabbedInterface, ObjectList,
                                                InlinePanel, PageChooserPanel, FieldRowPanel, MultiFieldPanel)
from wagtail.images.edit_handlers import ImageChooserPanel

from seo_page.models import SEOFields
from ..listings.models import PropertyListing
from ..listings import enums as listing_enums
from .forms import SuburbSearchForm


try:
    from schools.models import School
except ImportError:  # Schools is not part of the RE package so may not exist
    School = None


class SuburbPageGalleryItem(Orderable):
    page = ParentalKey('suburbs.SuburbPage', related_name='gallery')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        ImageChooserPanel('image')
    ]


class SuburbPageDwellingStats(Orderable):
    page = ParentalKey('suburbs.SuburbPage', related_name='dwelling_demos')
    dwelling_type = models.CharField("Type", max_length=255)
    percentage = models.FloatField(
        default=1.0,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ]
    )
    panels = [
        FieldRowPanel([
            FieldPanel('dwelling_type'),
            FieldPanel('percentage'),
        ])
    ]


class SuburbPageSimilarSuburbs(Orderable):
    page = ParentalKey('suburbs.SuburbPage', related_name='similar_suburbs')
    suburb = models.ForeignKey('suburbs.SuburbPage', related_name='like_suburbs', on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('suburb', 'suburbs.SuburbPage')
    ]


class SuburbPage(SEOFields, Page):
    STATE_NSW = 'nsw'
    STATE_ACT = 'act'
    STATE_QLD = 'qld'
    STATE_VIC = 'vic'
    STATE_TAS = 'tas'
    STATE_SA = 'sa'
    STATE_NT = 'nt'
    STATE_WA = 'wa'

    STATE_CHOICES = [
        (STATE_NSW, 'New South Wales'),
        (STATE_VIC, 'Victoria'),
        (STATE_QLD, 'Queensland'),
        (STATE_ACT, 'Australian Capital Territory'),
        (STATE_TAS, 'Tasmania'),
        (STATE_SA, 'South Australia'),
        (STATE_WA, 'Western Australia'),
        (STATE_NT, 'Northern Territory')
    ]

    state = models.CharField(max_length=10, blank=True, default="", choices=STATE_CHOICES)
    postcode = models.CharField(max_length=4, blank=True, default="")
    description = RichTextField(blank=True, default="")
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    featured_video_url = models.URLField(blank=True, default="",
                                         help_text="Youtube or Vimeo URL to a video about your office")

    # Demographics fields - will be separate tab in CMS
    population = models.IntegerField(default=0)
    median_age = models.DecimalField(decimal_places=1, max_digits=4, default=0.0)
    average_beds = models.DecimalField(decimal_places=1, max_digits=4, default=0.0)
    household_income = models.IntegerField(default=0)
    mortgage_repayments = models.IntegerField(default=0)

    # Hard coded upper limits for the charts on the page
    MAX_HOUSEHOLD_INCOME = 3500
    MAX_REPAYMENTS = 4000

    demographics_panels = [
        MultiFieldPanel([
            FieldPanel('population'),
            FieldPanel('median_age')
        ], "Population"),
        MultiFieldPanel([
            FieldPanel('household_income'),
            FieldPanel('mortgage_repayments')
        ], "Finances"),
        MultiFieldPanel([
            FieldPanel('average_beds'),
        ], "Dwellings"),
        InlinePanel('dwelling_demos', label="Dwelling Breakdown")
    ]

    parent_page_types = ['suburbs.SuburbIndex', 'suburbs.RegionPage']
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('state'),
                FieldPanel('postcode')
            ])], "Location"),
        ImageChooserPanel('featured_image'),
        FieldPanel('description'),
        FieldPanel('featured_video_url'),
        InlinePanel('gallery', label="Gallery"),
        InlinePanel('similar_suburbs', label="Similar Suburbs")
    ]

    @property
    def listings(self):
        return PropertyListing.objects.filter(address_suburb=self.title)

    @property
    def latest_listings(self):
        return self.listings.filter(status=listing_enums.STATUS_CURRENT).order_by('-created')

    @property
    def latest_sale_listings(self):
        return self.latest_listings.filter(
            models.Q(listing_type=listing_enums.LISTING_TYPE_SALE) |
            models.Q(listing_type=listing_enums.LISTING_TYPE_BOTH)
        )

    @property
    def latest_rent_listings(self):
        return self.latest_listings.filter(
            models.Q(listing_type=listing_enums.LISTING_TYPE_LEASE) |
            models.Q(listing_type=listing_enums.LISTING_TYPE_BOTH)
        )

    @property
    def latest_sold_listings(self):
        return self.listings.filter(
            status=listing_enums.STATUS_SOLD
        ).order_by('-soldDetails_date')

    @property
    def dwelling_chart_data(self):
        dwellings = self.dwelling_demos.all()
        if dwellings:
            labels, data = zip(*[(x.dwelling_type, x.percentage) for x in dwellings])
            return json.dumps({'labels': labels, 'data': data})
        return ''

    def schools(self):
        try:
            return School.objects.filter(suburb__iexact=self.title, state__iexact=self.state)
        except Exception:
            return []
        return ''


SuburbPage.edit_handler = TabbedInterface([
    ObjectList(SuburbPage.content_panels, heading='Content'),
    ObjectList(SuburbPage.demographics_panels, heading='Demographics'),
    ObjectList(SuburbPage.promote_panels, heading='Promote'),
    ObjectList(SuburbPage.settings_panels, heading='Settings', classname="settings"),
    ObjectList(SuburbPage.seo_panels, heading='SEO'),
])


class RegionPageGalleryItem(Orderable):
    page = ParentalKey('suburbs.RegionPage', related_name='gallery')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        ImageChooserPanel('image')
    ]


class RegionPage(SEOFields, Page):
    description = RichTextField(blank=True, default="")
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    featured_video_url = models.URLField(blank=True, default="",
                                         help_text="Youtube or Vimeo URL to a video about your office")
    subpage_types = ['suburbs.SuburbPage']

    content_panels = Page.content_panels + [
        ImageChooserPanel('featured_image'),
        FieldPanel('description'),
        FieldPanel('featured_video_url'),
        InlinePanel('gallery', label="Gallery")
    ]

    @property
    def suburbs(self):
        return SuburbPage.objects.live().descendant_of(self).order_by('title')

    @property
    def listings(self):
        suburb_titles = self.suburbs.values_list('title', flat=True)
        return PropertyListing.objects.filter(address_suburb__in=suburb_titles)

    @property
    def latest_listings(self):
        return self.listings.filter(status=listing_enums.STATUS_CURRENT).order_by('-created')

    @property
    def latest_sale_listings(self):
        return self.latest_listings.filter(
            models.Q(listing_type=listing_enums.LISTING_TYPE_SALE) |
            models.Q(listing_type=listing_enums.LISTING_TYPE_BOTH)
        )

    @property
    def latest_rent_listings(self):
        return self.latest_listings.filter(
            models.Q(listing_type=listing_enums.LISTING_TYPE_LEASE) |
            models.Q(listing_type=listing_enums.LISTING_TYPE_BOTH)
        )

    @property
    def latest_sold_listings(self):
        return self.listings.filter(
            status=listing_enums.STATUS_SOLD
        ).order_by('-soldDetails_date')


RegionPage.edit_handler = TabbedInterface([
    ObjectList(RegionPage.content_panels, heading='Content'),
    ObjectList(RegionPage.promote_panels, heading='Promote'),
    ObjectList(RegionPage.settings_panels, heading='Settings', classname="settings"),
    ObjectList(RegionPage.seo_panels, heading='SEO'),
])


class SuburbIndexFeaturedSuburb(Orderable):
    index = ParentalKey('suburbs.SuburbIndex', related_name='featured_suburbs')
    suburb = models.ForeignKey('suburbs.SuburbPage', on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('suburb', 'suburbs.SuburbPage')
    ]


class SuburbIndex(SEOFields, Page):
    form_class = SuburbSearchForm
    subpage_types = ['suburbs.SuburbPage', 'suburbs.RegionPage']
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        ImageChooserPanel('featured_image'),
        InlinePanel('featured_suburbs', label="Featured Suburbs")
    ]

    def search_results(self, q):
        return {
            'suburbs': self.suburbs.search(q),
            'regions': self.regions.search(q)
        }

    @property
    def suburbs(self):
        return SuburbPage.objects.live().descendant_of(self).order_by('title')

    @property
    def regions(self):
        return RegionPage.objects.live().descendant_of(self).order_by('title')

    def get_context(self, request, *args, **kwargs):
        context = super(SuburbIndex, self).get_context(request, *args, **kwargs)
        context['form'] = self.form_class(request.GET)
        context['suburbs'] = self.suburbs
        if context['form'].is_valid():
            context['suburbs'] = context['form'].as_search(self.suburbs)
        return context


SuburbIndex.edit_handler = TabbedInterface([
    ObjectList(SuburbIndex.content_panels, heading='Content'),
    ObjectList(SuburbIndex.promote_panels, heading='Promote'),
    ObjectList(SuburbIndex.settings_panels, heading='Settings', classname="settings"),
    ObjectList(SuburbIndex.seo_panels, heading='SEO'),
])
