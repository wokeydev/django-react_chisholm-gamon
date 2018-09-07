from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from wagtailgeowidget.edit_handlers import GeoPanel
from wagtail.admin.edit_handlers import (RichTextField, FieldRowPanel, FieldPanel, MultiFieldPanel,
                                                InlinePanel, TabbedInterface, ObjectList, PageChooserPanel)


class School(gismodels.Model):
    unique_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    suburb = models.CharField(max_length=100, db_index=True)
    postcode = models.CharField(max_length=4)
    location = gismodels.PointField(null=True, blank=True)

    STATE_NSW = 'nsw'
    STATE_VIC = 'vic'
    STATE_QLD = 'qld'
    STATE_TAS = 'tas'
    STATE_SA = 'sa'
    STATE_NT = 'nt'
    STATE_ACT = 'act'
    STATE_WA = 'wa'

    STATE_CHOICES = (
        (STATE_NSW, "New South Wales"),
        (STATE_VIC, "Victoria"),
        (STATE_QLD, "Queensland"),
        (STATE_TAS, "Tasmania"),
        (STATE_SA, "South Australia"),
        (STATE_NT, "Northern Territory"),
        (STATE_ACT, "Australian Capital Territory"),
        (STATE_WA, "Western Australia"),
    )
    state = models.CharField(choices=STATE_CHOICES, max_length=3, db_index=True)
    school_level = models.CharField(max_length=50, blank=True, default="")
    SCHOOL_TYPE_PUBLIC = 'public'
    SCHOOL_TYPE_PRIVATE = 'private'
    SCHOOL_TYPE_CHOICES = (
        (SCHOOL_TYPE_PRIVATE, "Private"),
        (SCHOOL_TYPE_PUBLIC, "Public"),
    )

    school_type = models.CharField(max_length=50, choices=SCHOOL_TYPE_CHOICES, blank=True, default="")

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('address'),
            FieldPanel('suburb'),
            FieldRowPanel([
                FieldPanel('postcode'),
                FieldPanel('state')
            ])
        ], "School Details"),
        GeoPanel('location'),
        MultiFieldPanel([
            FieldPanel('school_level'),
            FieldPanel('school_type'),
        ], "Category Details")
    ]

    def __str__(self):
        return f'{self.name} ({self.suburb}, {self.state.upper()})'

    @classmethod
    def closest_to_listing(cls, listing, limit=10):
        return cls.objects.filter(
            location__distance_lte=(listing.location, D(km=15)))\
            .annotate(distance=Distance('location', listing.location))\
            .order_by('distance')[:limit]
