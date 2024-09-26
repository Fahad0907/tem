import jsonfield
from django.db import models
from lib.models import Model


class GeoDefinition(Model):
    node_name = models.TextField()
    node_parent = models.ForeignKey('self', on_delete=models.RESTRICT, blank=True, null=True)

    class Meta:
        db_table = 'geo_definition'
        ordering = ['id']

    def __str__(self):
        return self.node_name


class GeoData(Model):
    field_name = models.TextField()
    field_parent = models.ForeignKey('self', on_delete=models.RESTRICT, blank=True, null=True)
    field_type = models.ForeignKey(GeoDefinition, on_delete=models.RESTRICT)
    geocode = models.CharField(max_length=20, blank=True, null=True)
    geojson = jsonfield.JSONField(blank=True, default={})
    uploaded_file_path = models.CharField(max_length=256, blank=True, default='cd')
    status = models.IntegerField(blank=True, default=0)

    class Meta:
        db_table = 'geo_data'
        ordering = ['field_type', 'field_name']

    def __str__(self):
        return self.field_name


class Cluster(Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    loc = models.ForeignKey(GeoData, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
