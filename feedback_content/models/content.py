from django.db import models
from lib.models import Model
from lib import choices


class Content(Model):
    type = models.CharField(max_length=50, choices=choices.content_type_choice)
    name = models.CharField(max_length=255, blank=True, null=True)
    content_file = models.FileField(upload_to='content/', blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
