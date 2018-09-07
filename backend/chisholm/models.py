from django.db import models
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import StreamField
from wagtail.api import APIField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.admin.edit_handlers import (FieldPanel, MultiFieldPanel, PageChooserPanel,
                                         StreamFieldPanel, InlinePanel, TabbedInterface, ObjectList)
from seo_page.models import SEOFields
from modelcluster.fields import ParentalKey
from cms.blocks import AbsoluteImageRenditionField
from . import blocks
from . import enums


class HomePageHeroGalleryItem(Orderable):
    page = ParentalKey('chisholm.HomePage', related_name='hero_gallery')
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
        APIField('image', serializer=AbsoluteImageRenditionField('original')),
        APIField('image_cropped', serializer=AbsoluteImageRenditionField(enums.HOMEPAGE_HERO_CROPPED, source='image'))
    ]


class HomePageFeaturedListings(Orderable):
    MAX_FEATURE_LISTINGS = 2
    page = ParentalKey('chisholm.HomePage', related_name='featured_listings')
    listing = models.ForeignKey(
        'realestate.PropertyListing',
        on_delete=models.CASCADE,
        related_name='+'
    )
    panels = [
        SnippetChooserPanel('listing')
    ]

    api_fields = [
        APIField('listing')
    ]


class HomePage(SEOFields, Page):
    # above the fold
    tagline = models.CharField(max_length=255)
    cta_text = models.CharField(max_length=50, help_text='Call-to-Action button text')
    cta_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )

    # below the fold, streamfields
    content_sections = StreamField([
        ('newsletter_signup', blocks.NewsLetterSignupBlock()),
        ('why_choose_us', blocks.WhyChooseUsBlock()),
        ('twin_panel', blocks.TwinPanel())
    ])

    content_panels = [
        FieldPanel('title'),
        MultiFieldPanel([
            InlinePanel('hero_gallery', label='Images'),
            FieldPanel('tagline'),
            FieldPanel('cta_text'),
            FieldPanel('cta_link')
        ], "Hero Section"),
        InlinePanel('featured_listings', label='Featured Listings',
                    max_num=HomePageFeaturedListings.MAX_FEATURE_LISTINGS),
        StreamFieldPanel('content_sections')
    ]

    api_fields = [
        APIField('title'),
        APIField('hero_gallery'),
        APIField('tagline'),
        APIField('cta_text'),
        APIField('cta_link'),
        APIField('featured_listings'),
        APIField('content_sections')
    ]


HomePage.edit_handler = TabbedInterface([
    ObjectList(HomePage.content_panels, heading='Content'),
    ObjectList(HomePage.promote_panels, heading='Promote'),
    ObjectList(HomePage.settings_panels, heading='Settings', classname="settings"),
    ObjectList(HomePage.seo_panels, heading='SEO'),
])
