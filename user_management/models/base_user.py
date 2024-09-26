from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from lib.models import BasicModel


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, is_staff=False, is_superuser=False, is_active=True):
        if not username:
            raise ValueError('Users must have a username')
        if not password:
            raise ValueError('Users must have a password')

        user_obj = self.model(username=username, is_staff=is_staff, is_superuser=is_superuser)
        user_obj.is_active = is_active
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        user_obj.save()

        return user_obj

    def create_staffuser(self, username, password=None):
        return self.create_user(username=username, password=password, is_staff=True)

    def create_superuser(self, username, password=None):
        return self.create_user(username=username, password=password, is_superuser=True, is_staff=True)


class User(AbstractBaseUser, PermissionsMixin, BasicModel):
    username = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(blank=True, default=True)

    is_staff = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.SET_NULL, related_name="user_created_by"
    )
    updated_by = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.SET_NULL, related_name="user_updated_by"
    )
    deleted_by = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.SET_NULL, related_name="user_deleted_by"
    )

    USERNAME_FIELD = 'username'

    objects = UserManager()

    def __str__(self):
        return self.username