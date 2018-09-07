from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.api import APIField
from wagtail.search import index
from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.api.fields import ImageRenditionField
from wagtail.admin.edit_handlers import (RichTextField, FieldRowPanel, FieldPanel, MultiFieldPanel,
                                         InlinePanel, TabbedInterface, ObjectList)

from seo_page.models import SEOFields
from ..enquiries.models import EnquiryFormPage
from ..listings.models import PropertyListing
from ..listings import enums as listing_enums
from ..agents.models import AgentPage
from ..testimonials.models import Testimonial


class OfficeBase(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    source_id = models.CharField(max_length=50, blank=True, default="")
    office_name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=100, blank=True, default="")
    suburb = models.CharField(max_length=50, blank=True, default="")
    postcode = models.CharField(max_length=5, blank=True, default="")
    state = models.CharField(max_length=50, blank=True, default="")

    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)

    phone = models.CharField(max_length=20, blank=True, default="")
    fax = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")

    facebook_url = models.URLField(blank=True, default="")
    linkedin_url = models.URLField(blank=True, default="")
    instagram_handle = models.CharField(max_length=50, blank=True, default="",
                                        help_text="Your Instagram username, without the @")
    twitter_handle = models.CharField(max_length=50, blank=True, default="",
                                      help_text="Your Twitter username, without the @")
    youtube_url = models.URLField(blank=True, default="")

    def __unicode__(self):
        return self.office_name

    class Meta:
        abstract = True


class OfficePage(SEOFields, EnquiryFormPage, OfficeBase):
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
    email_template = "email/office_enquiry.html"

    content_panels = Page.content_panels + [
        ImageChooserPanel('featured_image'),
        FieldPanel('office_name'),
        FieldPanel('description'),
        MultiFieldPanel([
            FieldPanel('address'),
            FieldPanel('suburb'),
            FieldPanel('postcode'),
            FieldPanel('state'),
            FieldPanel('latitude'),
            FieldPanel('longitude'),
        ], "Location"),
        MultiFieldPanel([
            FieldPanel('phone'),
            FieldPanel('fax'),
            FieldPanel('email'),
        ], "Contact Details"),
        MultiFieldPanel([
            FieldPanel('facebook_url'),
            FieldPanel('linkedin_url'),
            FieldPanel('instagram_handle'),
            FieldPanel('twitter_handle'),
            FieldPanel('youtube_url'),
        ], "Social Media Accounts"),
        InlinePanel('opening_hours', label="Opening Hours"),
        InlinePanel('servicing_postcodes', label="Servicing Postcodes"),
        InlinePanel('gallery', label="Image Gallery")
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('source_id')
    ]

    search_fields = Page.search_fields + [
        index.SearchField('office_name', partial_match=True),
        index.SearchField('suburb', partial_match=True),
        index.SearchField('postcode')
    ]

    parent_page_types = ['offices.OfficeIndexPage']

    api_fields = [
        APIField('title'),
        APIField('slug'),
        APIField('source_id'),
        APIField('office_name'),
        APIField('address'),
        APIField('suburb'),
        APIField('postcode'),
        APIField('state'),
        APIField('latitude'),
        APIField('longitude'),
        APIField('phone'),
        APIField('fax'),
        APIField('email'),
        APIField('facebook_url'),
        APIField('linkedin_url'),
        APIField('instagram_handle'),
        APIField('twitter_handle'),
        APIField('youtube_url'),
        APIField('description'),
        APIField('featured_image'),
        APIField('featured_video_url'),
        APIField('opening_hours'),
        APIField('gallery'),
        APIField('servicing_postcodes'),
    ]

    def get_email_subject(self):
        return "WEBSITE OFFICE ENQUIRY: %s" % self.title

    def get_recipients(self):
        recipients = super().get_recipients()
        recipients.append(self.email)
        return recipients

    def get_listings(self):
        # If the office has servicing postcodes, we are getting
        # those listings instead
        servicing_postcodes = self.servicing_postcodes.all().values_list('postcode', flat=True)
        if servicing_postcodes:
            return PropertyListing.objects.filter(address_postcode__in=list(servicing_postcodes))

        return PropertyListing.objects.filter(
            agents__agent__offices__office=self
        )

    @property
    def latest_listings_forsale(self):
        return self.get_listings().filter(
            status=listing_enums.STATUS_CURRENT,
            listing_type=listing_enums.LISTING_TYPE_SALE
        ).order_by('-created')

    @property
    def latest_listings_forrent(self):
        return self.get_listings().filter(
            status=listing_enums.STATUS_CURRENT,
            listing_type=listing_enums.LISTING_TYPE_LEASE
        ).order_by('-created')

    @property
    def latest_listings_sold(self):
        return self.get_listings().filter(
            status=listing_enums.STATUS_SOLD
        ).order_by('-created')

    @property
    def agents(self):
        return AgentPage.objects.filter(offices__office=self)

    @property
    def all_testimonials(self):
        return Testimonial.objects.filter(offices__office=self)

    def get_listing_sections(self):
        sections = [
            {
                'title': 'Latest listings for sale',
                'prop': 'latest_listings_forsale',
                # SETDATA url
                'url': '/buying/',
                'link_text': 'View all listings for sale',
            },
            {
                'title': 'Latest listings for rent',
                'prop': 'latest_listings_forrent',
                # SETDATA url
                'url': '/renting/',
                'link_text': 'View all listings for rent',
            },
            {
                'title': 'Latest sold properties',
                'prop': 'latest_listings_sold',
                # SETDATA url
                'url': '/selling/sold-properties/',
                'link_text': 'View all sold properties',
            }
        ]
        result = []
        for sec in sections:
            listings = getattr(self, sec['prop'])
            if listings:
                sec['listings'] = listings
                result.append(sec)
        return result


OfficePage.edit_handler = TabbedInterface([
    ObjectList(OfficePage.content_panels, heading='Content'),
    ObjectList(OfficePage.promote_panels, heading='Promote'),
    ObjectList(OfficePage.settings_panels, heading='Settings', classname="settings"),
    ObjectList(OfficePage.seo_panels, heading='SEO'),
])


class OpeningHours(models.Model):
    day = models.CharField(max_length=100)
    times = models.CharField(max_length=100)

    panels = [
        FieldRowPanel([
            FieldPanel('day', classname="col5"),
            FieldPanel('times', classname="col7"),
        ])
    ]

    class Meta:
        abstract = True


class OfficeOpeningHours(Orderable, OpeningHours):
    opening_hours = ParentalKey('offices.OfficePage', related_name='opening_hours')

    api_fields = [
        APIField('day'),
        APIField('times'),
    ]


class OfficePageGalleryItem(Orderable):
    page = ParentalKey('offices.OfficePage', related_name='gallery')
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
    api_fields = [
        APIField('image')
    ]


class OfficeServicingPostCodes(Orderable):
    page = ParentalKey('offices.OfficePage', related_name='servicing_postcodes')
    postcode = models.IntegerField()

    panels = [
        FieldPanel('postcode')
    ]

    api_fields = [
        APIField('postcode')
    ]


class OfficeGroup(models.Model):
    group_name = models.CharField(max_length=255, unique=True)
    offices = models.ManyToManyField('offices.OfficePage')


class OfficeIndexPage(SEOFields, EnquiryFormPage, Page):
    subpage_types = ['offices.OfficePage']

    def get_context(self, request, *args, **kwargs):
        context = super(OfficeIndexPage, self).get_context(request, *args, **kwargs)
        context['offices'] = self.offices
        return context

    @property
    def offices(self):
        return OfficePage.objects.live().descendant_of(self).order_by('office_name')


OfficeIndexPage.edit_handler = TabbedInterface([
    ObjectList(OfficeIndexPage.content_panels, heading='Content'),
    ObjectList(OfficeIndexPage.promote_panels, heading='Promote'),
    ObjectList(OfficeIndexPage.settings_panels, heading='Settings', classname="settings"),
    ObjectList(OfficeIndexPage.seo_panels, heading='SEO'),
])
