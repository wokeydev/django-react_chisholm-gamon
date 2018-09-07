"""
formbuilder_filefield.

Extends Wagtail's "form builder" to supply an Image upload or Document (i.e PDF) upload field.
Adapted from https://stackoverflow.com/questions/47927549/how-can-i-add-an-upload-file-field-to-a-wagtail-form

To use, inherit your form page from formbuilder_filefield.FormPage
"""

import json
from django.utils.translation import ugettext as _
from django.db import models
from django.shortcuts import render
from django.forms import FileField
from django.core.serializers.json import DjangoJSONEncoder

from modelcluster.fields import ParentalKey
from wagtail.contrib.forms.models import AbstractFormField, AbstractEmailForm, FORM_FIELD_CHOICES
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.images.fields import WagtailImageField
from wagtail.images import get_image_model
from wagtail.documents.models import get_document_model
from wagtail.admin.edit_handlers import (RichTextField, FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel,
                                         TabbedInterface, ObjectList)

from seo_page.models import SEOFields


def filename_to_title(filename):
    from os.path import splitext
    if filename:
        result = splitext(filename)[0]
        result = result.replace('-', ' ').replace('_', ' ')
        return result.title()


class FormField(AbstractFormField):
    FORM_FIELD_CHOICES = list(FORM_FIELD_CHOICES) + [
        ('image', 'Upload Image'),
        ('document', 'Upload Document')
    ]

    field_type = models.CharField(
        verbose_name=_('field type'),
        max_length=16,
        choices=FORM_FIELD_CHOICES)
    page = ParentalKey('FormPage', related_name='form_fields')


class ExtendedFormBuilder(FormBuilder):
    def create_image_field(self, field, options):
        return WagtailImageField(**options)

    def create_document_field(self, field, options):
        return FileField(**options)


class FormPage(SEOFields, AbstractEmailForm):
    form_builder = ExtendedFormBuilder

    def serve(self, request, *args, **kwargs):
        if request.method == 'POST':
            # form = self.get_form(request.POST, page=self, user=request.user)  # Original line
            form = self.get_form(request.POST, request.FILES, page=self, user=request.user)

            if form.is_valid():
                self.process_form_submission(form)
                context = self.get_context(request)
                context['success'] = True
                return render(
                    request,
                    self.get_landing_page_template(request),
                    context
                )
        else:
            form = self.get_form(page=self, user=request.user)

        context = self.get_context(request)
        context['form'] = form
        return render(
            request,
            self.get_template(request),
            context
        )

    def process_form_submission(self, form):
        cleaned_data = form.cleaned_data

        for name, field in form.fields.iteritems():
            if isinstance(field, WagtailImageField):
                image_file_data = cleaned_data[name]
                if image_file_data:
                    ImageModel = get_image_model()
                    image = ImageModel(
                        file=cleaned_data[name],
                        title=filename_to_title(cleaned_data[name].name),
                        collection=self.upload_image_to_collection,
                        # assumes there is always a user - will fail otherwise
                        uploaded_by_user=form.user,
                    )
                    image.save()
                    cleaned_data.update({name: image.id})
                else:
                    # remove the value from the data
                    del cleaned_data[name]
            elif isinstance(field, FileField):
                document_file_data = cleaned_data[name]
                if document_file_data:
                    DocumentModel = get_document_model()
                    document = DocumentModel(
                        file=cleaned_data[name],
                        title=filename_to_title(cleaned_data[name].name),
                        # assumes there is always a user - will fail otherwise
                        uploaded_by_user=form.user,
                    )
                    document.save()
                    cleaned_data.update({name: document.id})
                else:
                    # remove the value from the data
                    del cleaned_data[name]

        form_data = json.dumps(cleaned_data, cls=DjangoJSONEncoder)
        submission_object = dict(
            page=self,
            form_data=form_data,
            user=form.user,
        )

        return self.get_submission_class().objects.create(**submission_object)

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)


FormPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel('form_fields', label="Form fields"),
    FieldPanel('thank_you_text', classname="full"),
    MultiFieldPanel([
        FieldRowPanel([
            FieldPanel('from_address', classname="col6"),
            FieldPanel('to_address', classname="col6"),
        ]),
        FieldPanel('subject'),
    ], "Email"),
]

FormPage.edit_handler = TabbedInterface([
    ObjectList(FormPage.content_panels, heading='Content'),
    ObjectList(FormPage.promote_panels, heading='Promote'),
    ObjectList(FormPage.settings_panels, heading='Settings', classname="settings"),
    ObjectList(FormPage.seo_panels, heading='SEO'),
])
