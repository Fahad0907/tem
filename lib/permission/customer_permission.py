from rest_framework import permissions
from user_management import models as user_management_model


class PermissionManager(permissions.BasePermission):
    def __init__(self):
        self.module = None
        self.action = None

    def has_permission(self, request, view):
        if hasattr(view, 'module'):
            self.module = view.module

        if hasattr(view, 'action'):
            self.action = view.action

        # superuser can access all
        if request.user.is_superuser:
            return True

        try:
            user_role_instance = user_management_model.UserRole.objects.get(user=request.user)
            role_instance = user_management_model.Role.objects.get(role_name=user_role_instance.role.role_name)

            module_action_instance = user_management_model.ModuleActionMap.objects.get(
                module__module_name=self.module,
                action__action_name=self.action)
            role_module_action_instance = user_management_model.RoleWithModuleActionMap.objects.get(
                role=role_instance,
                module_action_map=module_action_instance
            )
            print(role_module_action_instance)
            if role_module_action_instance.permission:
                return True
        except:
            return False
        return False
