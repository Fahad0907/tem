from django.contrib import admin
from meeting_action import models

# Register your models here.
admin.site.register(models.SubMeeting)
admin.site.register(models.ParentMeeting)
admin.site.register(models.Indicator)

