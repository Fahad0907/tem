from rest_framework import serializers
from user_management import models as user_management_models


class RoleDropDownSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_management_models.Role
        fields = ['id', 'role_name']


class RoleSerializer(serializers.ModelSerializer):
    total_user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = user_management_models.Role
        fields = ['id', 'role_name', 'total_user']

    def get_total_user(self, obj):
        user_role_instances = user_management_models.UserRole.objects.filter(
            deleted_at=None, role=obj
        )
        return len(user_role_instances)
