from rest_framework import serializers
from django.utils import timezone
from Activity_log import models as activity_log_models
from user_management import models as user_management_models


class ActivityLogSerializer(serializers.ModelSerializer):
    user_obj = serializers.SerializerMethodField(read_only=True)
    role = serializers.SerializerMethodField(read_only=True)
    date = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = activity_log_models.ActivityLog
        fields = ['id', 'user', 'message', 'role', 'user_obj', 'date', 'time']

    def get_user_obj(self, obj):
        try:
            profile_instance = user_management_models.UserModuleProfile.objects.get(user=obj.user)
            return profile_instance.first_name
        except:
            return {}

    def get_role(self, obj):
        try:
            role_instance = user_management_models.UserRole.objects.get(user=obj.user)
            return role_instance.role.role_name
        except:
            return {}

    def get_date(self, obj):
        local_datetime = timezone.localtime(obj.created_at)
        return local_datetime.date()

    def get_time(self, obj):
        local_datetime = timezone.localtime(obj.created_at)
        return local_datetime.strftime('%I:%M %p')
