from django.contrib import admin
from user_management import models as user_management_model

# Register your models here.
admin.site.register(user_management_model.Action)
admin.site.register(user_management_model.Module)
admin.site.register(user_management_model.Role)
admin.site.register(user_management_model.ModuleActionMap)
admin.site.register(user_management_model.RoleWithModuleActionMap)
admin.site.register(user_management_model.UserLoc)
admin.site.register(user_management_model.UserClinic)
admin.site.register(user_management_model.UserOrganization)
admin.site.register(user_management_model.UserRole)
admin.site.register(user_management_model.User)
admin.site.register(user_management_model.UserModuleProfile)
