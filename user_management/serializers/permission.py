from rest_framework import serializers
from user_management import models as user_management_models


class ModuleRoleActionSerializer(serializers.ModelSerializer):
    action_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = user_management_models.RoleWithModuleActionMap
        fields = ['id', 'module_action_map', 'role', 'permission', 'action_type']

    def get_action_type(self, obj):
        return {
            "id": obj.module_action_map.action.id,
            "name": obj.module_action_map.action.action_name
        }


class PermissionSerializer(serializers.ModelSerializer):
    action = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = user_management_models.Role
        fields = ['id', 'role_name', 'is_active', 'action']

    def get_action(self, obj):
        module_instances = user_management_models.Module.objects.filter(deleted_at=None, is_active=True)
        list= []
        for module in module_instances:
            module_role_action_instance = user_management_models.RoleWithModuleActionMap.objects.filter(
                deleted_at=None, role=obj, module_action_map__module__module_name=module.module_name
            )
            list.append({
                "module_name": module.module_name,
                "info": ModuleRoleActionSerializer(module_role_action_instance, many=True).data
            })

        return list

