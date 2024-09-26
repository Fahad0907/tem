from django.db import models
from lib.models import Model


class Clinic(Model):
    name = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ClinicLoc(Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    location = models.ForeignKey('location.GeoData', on_delete=models.CASCADE)

    def __str__(self):
        return "{}--{}".format(self.clinic.name, self.location.field_name)
