from django.db import models
from lib.models import Model
from user_management import models as user_management_model


class Module(Model):
    module_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.module_name

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super(Module, self).save(*args, **kwargs)

        if is_new:
            actions = Action.objects.filter(is_active=True, deleted_at=None)
            for action in actions:
                try:
                    module_action_map_instance = ModuleActionMap.objects.create(module=self, action=action)
                    roles = user_management_model.Role.objects.filter(is_active=True)
                    for role in roles:
                        user_management_model.RoleWithModuleActionMap.objects.create(
                            module_action_map=module_action_map_instance,
                            role=role
                        )
                except Exception as err:
                    print("exception in module table ==========", str(err))


class Action(Model):
    action_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.action_name


class ModuleActionMap(Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)

    def __str__(self):
        return '{}-{}'.format(self.module.module_name, self.action.action_name)
