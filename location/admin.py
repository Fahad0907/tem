from django.contrib import admin
from location import models as location_model

admin.site.register(location_model.GeoDefinition)
admin.site.register(location_model.GeoData)
admin.site.register(location_model.Cluster)
