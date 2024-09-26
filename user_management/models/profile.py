from django.db import models
from lib.models import Model
from lib.choices import gender
from user_management import models as user_management_model


class UserModuleProfile(Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='userprofile')
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=gender.GENDER_CHOICES, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    designation = models.TextField(blank=True, null=True)
    picture = models.ImageField(upload_to='users/profile-picture/', blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.user, self.designation if self.designation else 'N/A')


class Role(Model):
    role_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.role_name

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super(Role, self).save(*args, **kwargs)
        if is_new:
            module_role_maps = user_management_model.ModuleActionMap.objects.all()
            for module_role_map in module_role_maps:
                try:
                    RoleWithModuleActionMap.objects.create(role=self, module_action_map=module_role_map)
                except Exception as err:
                    print("Error in Role model ==========", str(err))


class RoleWithModuleActionMap(Model):
    module_action_map = models.ForeignKey('user_management.ModuleActionMap', on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.BooleanField(default=False)

    def __str__(self):
        return "{}-{}-{}--{}".format(self.role.role_name,
                                     self.module_action_map.module.module_name,
                                     self.module_action_map.action.action_name,
                                     "TRUE" if self.permission else "False"
                                     )


class UserReject(Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
