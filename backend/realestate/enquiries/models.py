from django.db import models
from django.conf import settings
from cms.models import AbstractFixedFormPage
from cms.utils import send_email_template


class ListingEnquiry(models.Model):
    listing = models.ForeignKey('realestate.PropertyListing', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, default="")
    email_address = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=25, blank=True, default="")
    message = models.TextField(blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True)
    sent_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    email_template = "email/listing_enquiry.html"
    email_subject = "Listing Enquiry"

    class Meta:
        ordering = ('-timestamp', )

    def __str__(self):
        return "Enquiry: %s (%s)" % (self.listing, self.timestamp.strftime("%Y-%m-%d %H:%M:%S"))

    def get_email_template(self):
        return self.email_template

    def get_email_subject(self):
        return "WEBSITE ENQUIRY: %s" % self.listing

    def get_from_email(self):
        return settings.DEFAULT_FROM_EMAIL

    def get_recipients(self):
        recipients = []
        for agent in self.listing.agents.all():
            if agent.agent and agent.agent.email:  # Through model handling
                recipients.append(agent.agent.email)
        return recipients

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)
        if created:
            send_email_template(
                self.get_email_subject(),
                self.get_from_email(),
                self.get_recipients(),
                self.get_email_template(),
                {'enquiry': self}
            )


class EnquiryFormPage(AbstractFixedFormPage):

    def get_form_class(self):
        # Done this way to prevent circular imports due to Wagtail heavy models.
        from .forms import PageEnquiryForm
        return PageEnquiryForm

    def get_email_template(self):
        return self.email_template

    def get_email_subject(self):
        return "WEBSITE ENQUIRY: %s" % self.title

    def get_from_email(self):
        return settings.DEFAULT_FROM_EMAIL

    def get_recipients(self):
        return []

    def process_form_submission(self, form):
        send_email_template(
            self.get_email_subject(),
            self.get_from_email(),
            self.get_recipients(),
            self.get_email_template(),
            {'form_data': form.cleaned_data, 'self': self, 'form': form}
        )
        return super().process_form_submission(form)

    class Meta:
        abstract = True
