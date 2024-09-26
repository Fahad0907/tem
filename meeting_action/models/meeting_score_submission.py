from django.db import models
from lib.models import Model
from meeting_action import models as meeting_action_models


class MeetingScoreMain(Model):
    meeting = models.ForeignKey(meeting_action_models.SubMeeting, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=255, blank=True, null=True)
    male = models.IntegerField(default=0)
    female = models.IntegerField(default=0)
    score_card_image = models.ImageField(upload_to="meeting/score_card", blank=True, null=True)
    attendance_sheet_image = models.ImageField(upload_to="meeting/attendance_sheet", blank=True, null=True)
    meeting_participant_image = models.ImageField(upload_to="meeting/attendance_sheet", blank=True, null=True)


class MeetingScoreIndicator(Model):
    main = models.ForeignKey(MeetingScoreMain, on_delete=models.CASCADE)
    indicator = models.ForeignKey('meeting_action.Indicator', on_delete=models.CASCADE)
    issue_against_indicator = models.TextField(blank=True, null=True)
    reason_for_scoring = models.TextField(blank=True, null=True)
    suggestion = models.TextField(blank=True)
    score = models.IntegerField(default=0)
