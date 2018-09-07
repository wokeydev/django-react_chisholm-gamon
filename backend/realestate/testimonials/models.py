import datetime
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from wagtail.snippets.models import register_snippet
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import (RichTextField, FieldPanel, InlinePanel, PageChooserPanel,
                                                TabbedInterface, ObjectList)

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.core.models import Orderable
from seo_page.models import SEOFields
from django.template.defaultfilters import slugify

from ..listings.models import PropertyListing
from ..agents.models import AgentPage
from .forms import NameFieldToSlugForm
# from ..offices.models import OfficePage


class TestimonialAgent(Orderable):
    testimonial = ParentalKey('Testimonial', related_name='agents', on_delete=models.CASCADE)
    agent = models.ForeignKey(AgentPage, related_name='testimonials', on_delete=models.CASCADE)

    panels = [PageChooserPanel('agent', 'agents.AgentPage')]


class TestimonialOffice(Orderable):
    testimonial = ParentalKey('Testimonial', related_name='offices', on_delete=models.CASCADE)
    office = models.ForeignKey('offices.OfficePage', related_name='testimonials', on_delete=models.CASCADE)

    panels = [PageChooserPanel('office', 'offices.OfficePage')]


@register_snippet
@python_2_unicode_compatible
class Testimonial(ClusterableModel):
    TYPE_SALE = 'Sale'
    TYPE_RENT = 'Rental'
    TYPE_COMMERCIAL = 'Commercial'
    TYPE_CHOICES = (
        (TYPE_SALE, TYPE_SALE),
        (TYPE_RENT, TYPE_RENT),
        (TYPE_COMMERCIAL, TYPE_COMMERCIAL),
    )
    testimonial_type = models.CharField(choices=TYPE_CHOICES, max_length=10, blank=True, default="")
    name = models.CharField(max_length=100, blank=True, default="")
    headline = models.CharField(max_length=150, blank=True, default="")
    comments = RichTextField(max_length=1500, blank=True, default="")
    slug = models.SlugField(help_text='URL Slug for display page. Must be unique.')
    date = models.DateField(blank=True, null=True, default=None)
    listing = models.ForeignKey(PropertyListing, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    video_url = models.URLField(blank=True, default="", help_text="Vimeo or Youtube embed URL")

    panels = [
        FieldPanel('date'),
        FieldPanel('name'),
        FieldPanel('testimonial_type'),
        FieldPanel('slug'),
        FieldPanel('headline'),
        FieldPanel('comments'),
        InlinePanel('agents', label="Agents"),
        InlinePanel('offices', label="Offices"),
        # FieldPanel('listing'),
        ImageChooserPanel('image'),
        FieldPanel('video_url'),
    ]

    base_form_class = NameFieldToSlugForm

    @property
    def agent(self):
        return AgentPage.objects.filter(testimonialagent__testimonial=self).first()

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Testimonial.objects.filter(slug=self.slug).exists():
                self.slug += '-' + datetime.date.today().strftime("%Y-%m-%d")
        super(Testimonial, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("testimonial_details_slug", kwargs={'slug': self.slug})
