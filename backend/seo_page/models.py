"""
seo_page. Custom subclass of hte core Wagtail "Page" model that incorporates a number of SEO fields.

Usage: Instead of sublassing wagtailcore.Page, use seo_page.Page
"""

import json
from django.db import models
from django.contrib.postgres.fields import JSONField
from wagtail.core.models import Page as WagtailPage
from wagtail.admin.edit_handlers import (TabbedInterface, ObjectList, FieldPanel, MultiFieldPanel)
from wagtail.api import APIField


class SEOFields(models.Model):

    # general
    canonical = models.URLField(blank=True, default="")
    title_tag = models.CharField(max_length=255, blank=True, default="")
    structured_data = JSONField(default={}, blank=True, help_text="json-ld Structured Data")

    # meta
    meta_title = models.CharField(max_length=255, blank=True, default="")
    meta_description = models.TextField(blank=True, default="")
    meta_keywords = models.TextField(blank=True, default="")

    # open graph
    # <meta property="og:title" content="Title Here" />
    # <meta property="og:type" content="article" />
    # <meta property="og:url" content="http://www.example.com/" />
    # <meta property="og:image" content="http://example.com/image.jpg" />
    # <meta property="og:description" content="Description Here" />

    og_title = models.CharField(max_length=255, blank=True, default="")
    og_type = models.CharField(max_length=50, blank=True, default="")
    og_url = models.URLField(blank=True, default="")
    og_img = models.URLField(blank=True, default="")
    og_description = models.TextField(blank=True, default="")

    # Twitter
    # <meta name="twitter:card" value="summary">
    # <meta name="twitter:site" content="@publisher_handle">
    # <meta name="twitter:title" content="Page Title">
    # <meta name="twitter:description" content="Page description less than 200 characters">
    # <meta name="twitter:creator" content="@author_handle">
    # <-- Twitter Summary card images must be at least 120x120px -->
    # <meta name="twitter:image" content="http://www.example.com/image.jpg">

    twitter_card = models.CharField(max_length=50, blank=True, default="", help_text="Type of Twitter card")
    twitter_site = models.CharField(max_length=50, blank=True, default="", help_text="@name of publisher")
    twitter_title = models.CharField(max_length=255, blank=True, default="")
    twitter_description = models.CharField(max_length=200, blank=True, default="")
    twitter_creator = models.CharField(max_length=50, blank=True, default="", help_text="@name of author")
    twitter_image = models.CharField(max_length=255, blank=True, default="",
                                     help_text="Images must be at least 120x120px")

    template_override = models.CharField(max_length=255, blank=True, default="",
                                         help_text="Load this specific page template")

    content_panels = WagtailPage.content_panels

    settings_panels = WagtailPage.settings_panels + [
        FieldPanel('template_override')
    ]

    seo_panels = [
        FieldPanel('canonical'),
        MultiFieldPanel([
            FieldPanel('meta_title'),
            FieldPanel('meta_description'),
            FieldPanel('meta_keywords'),
        ], heading="Meta tags"),
        MultiFieldPanel([
            FieldPanel('og_title'),
            FieldPanel('og_type'),
            FieldPanel('og_url'),
            FieldPanel('og_img'),
            FieldPanel('og_description'),
        ], heading="Open Graph / Facebook tags"),
        MultiFieldPanel([
            FieldPanel('twitter_card'),
            FieldPanel('twitter_site'),
            FieldPanel('twitter_title'),
            FieldPanel('twitter_description'),
            FieldPanel('twitter_creator'),
            FieldPanel('twitter_image'),
        ], heading="Twitter Card"),
        FieldPanel('structured_data')
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(WagtailPage.promote_panels, heading='Promote'),
        ObjectList(settings_panels, heading='Settings', classname="settings"),
        ObjectList(seo_panels, heading='SEO'),
    ])

    api_meta_fields = [
        APIField('canonical'),
        APIField('title_tag'),
        APIField('structured_data'),
        APIField('meta_title'),
        APIField('meta_description'),
        APIField('meta_keywords'),
        APIField('og_title'),
        APIField('og_type'),
        APIField('og_url'),
        APIField('og_img'),
        APIField('og_description'),
        APIField('twitter_card'),
        APIField('twitter_site'),
        APIField('twitter_title'),
        APIField('twitter_description'),
        APIField('twitter_creator'),
        APIField('twitter_image'),
    ]

    class Meta:
        abstract = True

    def get_template(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.ajax_template or self.template_override or self.template
        else:
            return self.template_override or self.template

    def get_structured_data_json(self):
        if self.structured_data:
            return json.dumps(self.structured_data)
        return "{}"
