from django.db import models
from lib.models import Model


class Feedback(Model):
    user = models.ForeignKey('user_management.User', models.CASCADE)
    uuid = models.CharField(max_length=500, blank=True, null=True)
    feedback_topic = models.TextField()
    feedback_description = models.TextField()
    is_replied = models.BooleanField(default=False)
