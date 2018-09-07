import datetime
from django.db import models
from seo_page.models import SEOFields
from modelcluster.fields import ParentalKey
from wagtail.core.models import Page, Orderable
from wagtail.contrib.forms.edit_handlers import FormSubmissionsPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import (RichTextField, FieldRowPanel, FieldPanel, MultiFieldPanel,
                                         InlinePanel, TabbedInterface, ObjectList, PageChooserPanel)
from cms.models import AbstractFixedFormPage
from .forms import CareerApplicationForm


class CareerPage(SEOFields, Page):
    JOB_TYPE_FULL = 'full'
    JOB_TYPE_PART = 'part'
    JOB_TYPE_CASUAL = 'casual'

    JOB_TYPE_CHOICES = [
        (JOB_TYPE_FULL, 'Full Time'),
        (JOB_TYPE_PART, 'Part Time'),
        (JOB_TYPE_CASUAL, 'Casual'),
    ]

    date_posted = models.DateField(blank=True, null=True, default=None, help_text="Used for Ordering")
    closing_date = models.DateField(blank=True, null=True, default=None,
                                    help_text="Position will stop displaying after this date")
    job_name = models.CharField(max_length=255, help_text="Name of the Job Position")
    job_type = models.CharField(max_length=10, choices=JOB_TYPE_CHOICES)
    location = models.ForeignKey('offices.OfficePage', on_delete=models.SET_NULL, blank=True, null=True, default=None)
    description = RichTextField(blank=True, default="")

    content_panels = [
        FieldPanel('job_name'),
        FieldPanel('title'),
        FieldPanel('job_type'),
        FieldPanel('description'),
        FieldRowPanel([
            FieldPanel('date_posted'),
            FieldPanel('closing_date')
        ]),
        PageChooserPanel('location', 'offices.OfficePage'),
    ]

    class Meta:
        ordering = ['-date_posted']

    def save(self, *args, **kwargs):
        if not self.pk and not self.date_posted:
            self.date_posted = datetime.date.today()
        super(CareerPage, self).save(*args, **kwargs)


CareerPage.edit_handler = TabbedInterface([
    ObjectList(CareerPage.content_panels, heading='Content'),
    ObjectList(CareerPage.promote_panels, heading='Promote'),
    ObjectList(CareerPage.settings_panels, heading='Settings', classname="settings"),
    ObjectList(CareerPage.seo_panels, heading='SEO'),
])


class CareerIndexPageGalleryItem(Orderable):
    page = ParentalKey('careers.CareerIndexPage', related_name='gallery_items')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )


class CareerPageCheckMarkItem(Orderable):
    page = ParentalKey('careers.CareerIndexPage', related_name='checkmark_items')
    title = models.CharField(max_length=25)
    text = models.CharField(max_length=255, blank=True, default="")

    panels = [
        FieldPanel('title'),
        FieldPanel('text')
    ]


class CareerIndexPage(SEOFields, AbstractFixedFormPage):
    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    headline = RichTextField(help_text="Text across banner. Content marked as 'bold' will show pink")
    sub_headline = models.CharField(max_length=255, blank=True, default="",
                                    help_text="Displayed under the banner image")
    description = RichTextField(blank=True, default="", help_text="Displayed under the Sub Headline and Banner image")
    testimonial_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    testimonial_content = RichTextField(blank=True, default="")
    testimonial_name = models.CharField(max_length=255, blank=True, default="")
    testimonail_title = models.CharField(max_length=255, blank=True, default="")

    footer_headline = models.CharField(max_length=255, blank=True, default="",
                                       help_text="Displayed under the current positions")
    footer_content = RichTextField(blank=True, default="",
                                   help_text="Displayed under the Footer headline and Banner image")
    footer_cta_text = models.CharField("Footer Call-to-Action", max_length=50, blank=True, default="")

    subpage_types = ['careers.CareerPage']
    form_class = CareerApplicationForm

    content_panels = Page.content_panels + [
        FieldPanel('headline'),
        ImageChooserPanel('banner_image'),
        MultiFieldPanel([
            FieldPanel('sub_headline'),
            FieldPanel('description')
        ], "Bellow Banner"),
        InlinePanel('gallery_items', label="Gallery", max_num=3),
        InlinePanel('checkmark_items', label="Checkmarks", max_num=3),
        MultiFieldPanel([
            FieldPanel('testimonial_content'),
            FieldPanel('testimonial_name'),
            FieldPanel('testimonail_title'),
            ImageChooserPanel('testimonial_image'),
        ], "Testimonial"),
        MultiFieldPanel([
            FieldPanel('footer_headline'),
            FieldPanel('footer_content'),
            FieldPanel('footer_cta_text'),
        ], "Footer"),

    ]

    settings_panels = Page.settings_panels + [
        FormSubmissionsPanel()
    ]

    @property
    def careers(self):
        return CareerPage.objects.live().descendant_of(self).filter(closing_date__gte=datetime.date.today())


CareerIndexPage.edit_handler = TabbedInterface([
    ObjectList(CareerIndexPage.content_panels, heading='Content'),
    ObjectList(CareerIndexPage.promote_panels, heading='Promote'),
    ObjectList(CareerIndexPage.settings_panels, heading='Settings', classname="settings"),
    ObjectList(CareerIndexPage.seo_panels, heading='SEO'),
])
