from django.db import models
from lib.models import Model


class ActivityLog(Model):
    user = models.ForeignKey('user_management.User', on_delete=models.CASCADE)
    message = models.TextField()
    uuid = models.TextField(blank=True, null=True)
