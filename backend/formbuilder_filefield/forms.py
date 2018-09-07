"""
formbuilder_filefield.

Extends Wagtail's "form builder" to supply an Image upload or Document (i.e PDF) upload field.
Adapted from https://stackoverflow.com/questions/47927549/how-can-i-add-an-upload-file-field-to-a-wagtail-form

To use, inherit your form page from formbuilder_filefield.FormPage
"""

from wagtail.wagtailforms.models import AbstractFormField, FORM_FIELD_CHOICES
from wagtail.wagtailforms.forms import FormBuilder
from wagtail.wagtailimages.fields import WagtailImageField
from django.db import models

def filename_to_title(filename):
    from os.path import splitext
    if filename:
        result = splitext(filename)[0]
        result = result.replace('-', ' ').replace('_', ' ')
        return result.title()


class FormField(AbstractFormField):
    FORM_FIELD_CHOICES = list(FORM_FIELD_CHOICES) + [('image', 'Upload Image')]
    field_type = models.CharField(
        verbose_name=_('field type'),
        max_length=16,
        choices=FORM_FIELD_CHOICES)
    page = ParentalKey('FormPage', related_name='form_fields')


class ExtendedFormBuilder(FormBuilder):
    def create_image_upload_field(self, field, options):
        return WagtailImageField(**options)
    FIELD_TYPES = FormBuilder.FIELD_TYPES
    FIELD_TYPES.update({
        'image': create_image_upload_field,
    })


class FormPage(AbstractEmailForm):
    form_builder = ExtendedFormBuilder

    def serve(self, request, *args, **kwargs):
        if request.method == 'POST':
            # form = self.get_form(request.POST, page=self, user=request.user)  # Original line
            form = self.get_form(request.POST, request.FILES, page=self, user=request.user)

            if form.is_valid():
                self.process_form_submission(form)
                return render(
                    request,
                    self.get_landing_page_template(request),
                    self.get_context(request)
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

        form_data = json.dumps(cleaned_data, cls=DjangoJSONEncoder)
        submission_object = dict(
            page=self,
            form_data=form_data,
            user=form.user,
        )

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