import uuid
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from ..listings.forms import ListingSearchForm


class ActiveManager(models.Manager):
    """
    Custom manager to get only current subscribers
    """
    def get_queryset(self):
        return super().get_queryset().filter(unsubscribed=None)


class PropertyAlert(models.Model):
    """
    Storage of search preferences and emal details for sending a
    'property alert' - an email containing new relevant listings
    to a given user.
    """
    FREQUENCY_DAILY = 1
    FREQUENCY_WEEKLY = 7
    FREQUENCY_MONTHLY = 30

    FREQUENCY_CHOICES = [
        (FREQUENCY_DAILY, 'Daily'),
        (FREQUENCY_WEEKLY, 'Weekly'),
        (FREQUENCY_MONTHLY, 'Monthly'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Using an UUID so they can't be unsubscribed randomly.

    descriptive_name = models.CharField(max_length=255, default="Property Alert")
    email = models.EmailField()
    criteria = JSONField()
    frequency = models.IntegerField(choices=FREQUENCY_CHOICES, default=FREQUENCY_WEEKLY)
    last_sent = models.DateTimeField(null=True, blank=True, default=None)
    unsubscribed = models.DateTimeField(null=True, blank=True, default=None)

    subscribers = ActiveManager()
    objects = models.Manager()
    email_template = "email/property_alert.html"
    email_sender = settings.DEFAULT_FROM_EMAIL

    def get_new_listings(self):
        form = ListingSearchForm(self.criteria)
        if form.is_valid():
            return form.as_search(override_params={'created__gte': self.last_sent})

    def get_email_subject(self):
        return "Property Alert: %s" % self.descriptive_name

    def get_email_template(self):
        return self.email_template

    def __str__(self):
        return "<Alert> %s" % self.email

    def __unicode__(self):
        return u'<Alert> %s' % self.email


class PropertyAlertLog(models.Model):
    """
    A log of alert sends.
    """
    alert = models.ForeignKey('alerts.PropertyAlert', on_delete=models.CASCADE)
    sent = models.DateTimeField(auto_now_add=True)
    listings = models.IntegerField(default=0)
