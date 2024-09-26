from django.db import models
from lib.models import Model


class Organization(Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    email = models.EmailField(max_length=254)

    def __str__(self):
        return self.name

    @staticmethod
    def organization_instance(self, org_id):
        return Organization.objects.get(id=org_id)


class OrganizationLoc(Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    location = models.ForeignKey('location.GeoData', on_delete=models.CASCADE)

    def __str__(self):
        return '{}--{}'.format(self.organization.name, self.location.field_name)
