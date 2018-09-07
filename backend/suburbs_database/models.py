from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from wagtailgeowidget.edit_handlers import GeoPanel
from wagtail.admin.edit_handlers import (RichTextField, FieldRowPanel, FieldPanel, MultiFieldPanel,
                                                InlinePanel, TabbedInterface, ObjectList, PageChooserPanel)


class SuburbData(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    urban_area = models.CharField(max_length=50, blank=True, default="")
    state_code = models.CharField(max_length=3)
    state = models.CharField(max_length=50)
    postcode = models.CharField(max_length=4)
    type = models.CharField(max_length=25)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location = models.PointField(srid=4326, null=True, blank=True)
    elevation = models.IntegerField()
    population = models.IntegerField()
    area = models.DecimalField(max_digits=9, decimal_places=3)
    local_government_area = models.CharField(max_length=50)
    timezone = models.CharField(max_length=50)
    bordering_locations = ArrayField(models.IntegerField())

    panels = [
        FieldPanel('id'),
        FieldPanel('name'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('state_code'),
                FieldPanel('state'),
            ]),
            FieldPanel('postcode')
        ], "Location"),
        GeoPanel('location'),
        MultiFieldPanel([
            FieldPanel('type'),
            FieldPanel('elevation'),
            FieldPanel('population'),
            FieldPanel('area'),
            FieldPanel('local_government_area'),
            FieldPanel('timezone'),
        ], "Details"),
        FieldPanel('bordering_locations')
    ]

    class Meta:
        ordering = ['name']

    @property
    def surrounding(self):
        return SuburbData.objects.filter(id__in=self.bordering_locations)

    def save(self, *args, **kwargs):
        if not self.bordering_locations:
            self.bordering_locations = []
        if not self.location and (self.latitude and self.longitude):
            self.location = Point(float(self.longitude), float(self.latitude))
        super(SuburbData, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s %s %s" % (self.name, self.state, self.postcode)

    def __str__(self):
        return self.__unicode__()
