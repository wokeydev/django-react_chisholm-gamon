import json

from django import forms
from django.db import models
from django.http import Http404
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder

from modelcluster.fields import ParentalKey
from wagtail.documents.models import Document
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import (TabbedInterface, ObjectList, RichTextField, FieldPanel,
                                         InlinePanel, MultiFieldPanel, FieldRowPanel, PageChooserPanel,
                                         StreamFieldPanel)
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.core.models import Page, Orderable
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.contrib.forms.models import FormSubmission
from wagtail.core.fields import StreamField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.api import APIField
from modelcluster.models import ClusterableModel

from seo_page.models import SEOFields
from chisholm.blocks import SideBar
from .utils import send_email_template
from . import enums


class AbstractHTMLEmailForm(AbstractEmailForm):
    html_template = "email/form_page.html"

    def send_mail(self, form):
        addresses = [x.strip() for x in self.to_address.split(',')]
        content = []
        for field in form:
            value = field.value()
            if isinstance(value, list):
                value = ', '.join(value)
            content.append('{}: {}'.format(field.label, value))
        content = '\n'.join(content)
        send_email_template(
            self.subject,
            self.from_address,
            addresses,
            self.html_template,
            {'page': self, 'form': form}
        )

    class Meta:
        abstract = True


class ContentPageBase(Page):
    body = RichTextField()
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    sidebar = StreamField(SideBar(max_num=1, min_num=1, required=True))

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        ImageChooserPanel('featured_image'),
        StreamFieldPanel('sidebar')
    ]

    api_fields = [
        APIField('title'),
        APIField('body'),
        APIField('featured_image'),
        APIField('featured_image_cropped', serializer=ImageRenditionField(
            enums.CONTENT_IMAGE_CROP, source='featured_image')),
        APIField('sidebar')
    ]

    class Meta:
        abstract = True


# Generic Page
class ContentPage(SEOFields, ContentPageBase):
    content_panels = Page.content_panels + [
        FieldPanel('body'),
        ImageChooserPanel('featured_image'),
        StreamFieldPanel('sidebar')
    ]


ContentPage.edit_handler = TabbedInterface([
    ObjectList(ContentPage.content_panels, heading='Content'),
    ObjectList(ContentPage.promote_panels, heading='Promote'),
    ObjectList(ContentPage.settings_panels, heading='Settings', classname="settings"),
    ObjectList(ContentPage.seo_panels, heading='SEO'),
])


# Generic Form Page
class FormField(AbstractFormField):
    page = ParentalKey('ContentPageWithForm', related_name='form_fields')


class ContentPageWithForm(SEOFields, AbstractHTMLEmailForm):
    body = RichTextField()
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    sidebar = StreamField(SideBar(max_num=1, min_num=1, required=True))
    content_panels = ContentPageBase.content_panels + [
        InlinePanel('form_fields', label="Form fields"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]

    def get_landing_page_template(self, request, *args, **kwargs):
        return self.get_template(request, *args, **kwargs)

    def render_landing_page(self, request, form_submission=None, *args, **kwargs):
        """
        Override to provide a 'success' context variable.
        """
        context = self.get_context(request)
        context['success'] = True
        context['form_submission'] = form_submission
        return render(
            request,
            self.get_landing_page_template(request),
            context
        )


ContentPageWithForm.edit_handler = TabbedInterface([
    ObjectList(ContentPageWithForm.content_panels, heading='Content'),
    ObjectList(ContentPageWithForm.promote_panels, heading='Promote'),
    ObjectList(ContentPageWithForm.settings_panels, heading='Settings', classname="settings"),
    ObjectList(ContentPageWithForm.seo_panels, heading='SEO'),
])


class LinkBase(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Will add a structured data "logo" element'
    )
    link_description = RichTextField(blank=True, default="")
    link_title = models.CharField(max_length=255)

    @property
    def link(self):
        if self.link_page:
            return self.link_page.get_url()
        else:
            return self.link_external

    panels = [
        FieldPanel('link_title'),
        FieldPanel('link_description'),
        ImageChooserPanel('image'),
        MultiFieldPanel([
            FieldPanel('link_external'),
            PageChooserPanel('link_page'),
        ], "HREF Details")
    ]

    class Meta:
        abstract = True


class LinkLibraryLink(LinkBase, Orderable):
    page = ParentalKey('cms.LinkLibraryPage', related_name='links')

    api_fields = [
        APIField('link'),
    ]


class LinkLibraryPage(SEOFields, ContentPageBase):
    content_panels = ContentPageBase.content_panels + [
        InlinePanel('links', label="Links")
    ]

    api_fields = ContentPageBase.api_fields + [
        APIField('links')
    ]


LinkLibraryPage.edit_handler = TabbedInterface([
    ObjectList(LinkLibraryPage.content_panels, heading='Content'),
    ObjectList(LinkLibraryPage.promote_panels, heading='Promote'),
    ObjectList(LinkLibraryPage.settings_panels, heading='Settings', classname="settings"),
    ObjectList(LinkLibraryPage.seo_panels, heading='SEO'),
])


class iFramePage(SEOFields, Page):
    iframe_code = models.TextField(blank=True, default="",
                                   help_text="The full HTML code for the iframe embed")
    content_panels = Page.content_panels + [
        FieldPanel('iframe_code')
    ]

    api_fields = [
        APIField('iframe_code')
    ]


iFramePage.edit_handler = TabbedInterface([
    ObjectList(iFramePage.content_panels, heading='Content'),
    ObjectList(iFramePage.promote_panels, heading='Promote'),
    ObjectList(iFramePage.settings_panels, heading='Settings', classname="settings"),
    ObjectList(iFramePage.seo_panels, heading='SEO'),
])


class ProxyPage(Page):
    """
    Simple page type for redirecting. Used to place in the tree for menus.
    """
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )

    content_panels = [
        FieldPanel('title'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
    ]

    def serve(self, request):
        if self.link_page:
            return redirect(self.link_page.get_url())
        elif self.link_external:
            return redirect(self.link_external)
        raise Http404

    api_fields = [
        APIField('link_page'),
        APIField('link_external')
    ]


# Settings
@register_setting
class SocialMediaSettings(BaseSetting):
    facebook_url = models.URLField(blank=True, default="")
    linkedin_url = models.URLField(blank=True, default="")
    instagram_handle = models.CharField(max_length=50, blank=True, default="",
                                        help_text="Your Instagram username, without the @")
    twitter_handle = models.CharField(max_length=50, blank=True, default="",
                                      help_text="Your Twitter username, without the @")
    youtube_url = models.URLField(blank=True, default="")


@register_setting
class ThirdPartyApiSettings(BaseSetting):
    google_maps = models.CharField(max_length=255, blank=True, default="", help_text="Your Google maps API key")
    google_analytics = models.CharField(max_length=50, blank=True, default="",
                                        help_text="Your Google Analytics property/tracking ID. Formatted as UA-XXXXX-Y")
    google_tag_manager = models.CharField(max_length=50, blank=True, default="",
                                          help_text="Your Google Tag Manager container ID. Formatted as GTM-XXXX")
    facebook_pixel_id = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="The ID from your facebook pixel code. Can be found in the \"fbq('init',<CODE>)\" of the pixel code"
    )
    mandrill = models.CharField(max_length=255, blank=True, default="", help_text="Your Mandrill API key")
    mailgun = models.CharField(max_length=255, blank=True, default="", help_text="Your Mailgun API key")


@register_setting
class RobotsTxtSettings(BaseSetting):
    robots_txt = models.TextField(blank=True, default="", help_text="Content of your robots.txt file")

    class Meta:
        verbose_name = 'robots.txt'


class QuickLink(LinkBase, Orderable):
    setting = ParentalKey('cms.QuickLinkSettings', related_name='links')


@register_setting
class QuickLinkSettings(ClusterableModel, BaseSetting):
    panels = [
        InlinePanel('links', label="Links")
    ]


@register_setting
class SEOSettings(BaseSetting):
    contact_types = [
        'customer service',
        'technical support',
        'billing support',
        'bill payment',
        'sales',
        'reservations',
        'credit card support',
        'emergency',
        'baggage tracking',
        'roadside assistance',
        'package tracking'
    ]
    CONTACT_TYPE_CHOICES = [(i, i.title()) for i in contact_types]

    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Will add a structured data "logo" element'
    )
    customer_contact_number = models.CharField(max_length=25, blank=True, default="")
    customer_contact_type = models.CharField(
        max_length=50,
        blank=True,
        default="",
        choices=CONTACT_TYPE_CHOICES,
        help_text='Combined with Contact Number, will add "Organisation" structured data'
    )
    organisation_address = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text="Address to display in the Google 'smart result' box"
    )
    organisation_email = models.EmailField(blank=True, default="", help_text='General email address')
    organisation_name = models.CharField(max_length=255, blank=True, default="")

    panels = [
        MultiFieldPanel([
            ImageChooserPanel('logo'),
            FieldRowPanel([
                FieldPanel('customer_contact_number'),
                FieldPanel('customer_contact_type'),
            ]),
            FieldPanel('organisation_address'),
            FieldPanel('organisation_email')
        ], "Organisation Structured Data")
    ]


class AbstractFixedFormPage(Page):
    """
    A page model that includes a specific form class (as opposed to the form builder)
    """
    form_class = forms.Form

    class Meta:
        abstract = True

    def get_form_class(self):
        return self.form_class

    def get_form_kwargs(self, request=None):
        kwargs = {}
        if request and request.POST:
            kwargs = {'data': request.POST}
        return kwargs

    def get_form(self, request=None):
        return self.get_form_class()(**self.get_form_kwargs(request))

    def get_context(self, request, *args, **kwargs):
        context = super(AbstractFixedFormPage, self).get_context(request, *args, **kwargs)
        context['form'] = self.get_form(request)
        return context

    def get_submission_class(self):
        """
        Returns submission class.
        You can override this method to provide custom submission class.
        Your class must be inherited from AbstractFormSubmission.
        """

        return FormSubmission

    def process_form_submission(self, form):
        """
        Accepts form instance with submitted data, user and page.
        Creates submission instance.
        You can override this method if you want to have custom creation logic.
        For example, if you want to save reference to a user.
        """

        return self.get_submission_class().objects.create(
            form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
            page_id=self.page_ptr_id,
        )

    def handle_file_uploads(self, form, files):
        if not files:
            return
        for key, file in files.items():
            doc = Document(
                title=key,
                file=file,
            )
            doc.save()
            form.cleaned_data[key] = self.get_site.root_url + doc.url

    def serve(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = self.get_form(request)
            if form.is_valid():
                self.handle_file_uploads(form, request.FILES)

                self.process_form_submission(form)
                messages.success(request, "Thank you, enquiry submitted successfully")
                try:
                    form.save()  # if it has a save method we should call
                except AttributeError:  # No save method
                    pass

                context = self.get_context(request)
                context['success'] = True
                return render(
                    request,
                    self.get_template(request),
                    context
                )
        else:
            form = self.get_form(request)

        context = self.get_context(request)
        context['form'] = form
        return render(
            request,
            self.get_template(request),
            context
        )
