from django.db import models
from datetime import datetime
from user_management import models as user_management_model


class BasicModel(models.Model):
    """
    Time trackers
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    last_sync = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class Model(BasicModel):
    """
    User trackers
    """

    created_by = models.ForeignKey('user_management.User', blank=True, null=True,
                                   on_delete=models.SET_NULL, related_name="created_by_%(class)ss")
    updated_by = models.ForeignKey('user_management.User', blank=True, null=True,
                                   on_delete=models.SET_NULL, related_name="updated_by_%(class)ss")
    deleted_by = models.ForeignKey('user_management.User', blank=True, null=True,
                                   on_delete=models.SET_NULL, related_name="deleted_by_%(class)ss")

    class Meta:
        abstract = True
