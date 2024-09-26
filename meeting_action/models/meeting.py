from django.db import models
from lib.models import Model
from lib import choices


class ParentMeeting(Model):
    community_clinic = models.ForeignKey('clinic.Clinic', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    uuid = models.CharField(max_length=255, unique=True)
    datetime = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{}-{}".format(self.community_clinic.name, self.name)


class SubMeeting(Model):
    schedule = models.ForeignKey(ParentMeeting, on_delete=models.CASCADE)
    meeting_level = models.CharField(choices=choices.meeting_level_choices, max_length=50)
    village_name = models.CharField(max_length=255, null=True, blank=True)
    venue_name = models.CharField(max_length=255, null=True, blank=True)
    meeting_status = models.CharField(max_length=255, choices=choices.meeting_status_choices)
    datetime = models.DateTimeField(blank=True, null=True)
    uuid = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "{}-{}-{}".format(self.schedule.name, self.meeting_level, self.venue_name)
