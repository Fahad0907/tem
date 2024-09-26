from django.db import models
from lib.models import Model


class UserLoc(Model):
    user = models.ForeignKey('user_management.User', on_delete=models.CASCADE)
    location = models.ForeignKey('location.GeoData', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class UserOrganization(Model):
    user = models.ForeignKey('user_management.User', on_delete=models.CASCADE)
    organization = models.ForeignKey('organization.organization', on_delete=models.CASCADE)

    def __str__(self):
        return "{}--{}".format(self.user.username, self.organization.name)


class UserClinic(Model):
    user = models.ForeignKey('user_management.User', on_delete=models.CASCADE)
    clinic = models.ForeignKey('clinic.Clinic', on_delete=models.CASCADE)

    def __str__(self):
        return "{}--{}".format(self.user.username, self.clinic.name)


class UserRole(Model):
    user = models.ForeignKey('user_management.User', on_delete=models.CASCADE)
    role = models.ForeignKey('user_management.Role', on_delete=models.CASCADE)

    def __str__(self):
        return "{}--{}".format(self.user.username, self.role.role_name)
