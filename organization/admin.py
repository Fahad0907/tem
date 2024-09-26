from django.contrib import admin
from organization import models as organization_model


admin.site.register(organization_model.Organization)
admin.site.register(organization_model.OrganizationLoc)
