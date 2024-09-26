from django.db import models
from lib.models import Model
from lib import choices
from meeting_action import models as meeting_action_model


class Actions(Model):
    meeting = models.ForeignKey(meeting_action_model.SubMeeting, on_delete=models.CASCADE)
    indicator = models.ForeignKey(meeting_action_model.Indicator, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=500, blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=255, choices=choices.action_status_type_choice, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    supervisor = models.CharField(max_length=255, blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True, null=True)

