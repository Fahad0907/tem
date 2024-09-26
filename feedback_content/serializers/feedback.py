from rest_framework import serializers
from django.utils import timezone
from feedback_content import models as feedback_content_models
from user_management import models as user_management_models


class FeedbackSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)
    user_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = feedback_content_models.Feedback
        fields = ['id', 'feedback_topic', 'feedback_description', 'is_replied', 'user', 'uuid', 'date', 'time',
                  'user_info', 'created_at']

        extra_kwargs = {
            'uuid': {
                'required': True
            },
            'created_at': {
                'read_only': True
            }
        }

    def get_date(self, obj):
        local_datetime = timezone.localtime(obj.created_at)
        return local_datetime.date()

    def get_time(self, obj):
        local_datetime = timezone.localtime(obj.created_at)
        return local_datetime.strftime('%I:%M %p')

    def get_user_info(self, obj):
        try:
            user_instance = user_management_models.User.objects.get(id=obj.user.id)
            user_roles = user_management_models.UserRole.objects.get(user=user_instance)

            return {
                "user_name": user_instance.userprofile.first_name,
                "role": user_roles.role.role_name
            }
        except:
            return {}
