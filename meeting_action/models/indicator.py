from django.db import models
from lib.models import Model


class Indicator(Model):
    name = models.TextField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
