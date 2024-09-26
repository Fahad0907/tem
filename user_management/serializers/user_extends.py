from rest_framework import serializers
from user_management import models as user_management_model


class UserOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_management_model.UserOrganization
        fields = ['id', 'user', 'organization']


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_management_model.UserLoc
        fields = ['id', 'user', 'location']


class UserClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_management_model.UserClinic
        fields = ['id', 'user', 'clinic']


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_management_model.UserRole
        fields = ['id', 'user', 'role']
