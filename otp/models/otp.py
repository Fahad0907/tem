from django.db import models
from lib.models import Model
from lib.choices import otp_type


class Otp(Model):
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    type = models.CharField(choices=otp_type.OTP_CHOICES, max_length=20)
    code = models.CharField(max_length=20)
    time = models.DateTimeField(auto_now_add=True)
    is_checked = models.BooleanField(default=False)

    def __str__(self):
        return "{}-{}-{}-{}".format(self.email if self.email else "N/A",
                                    self.phone if self.phone else "N/A",
                                    self.type,
                                    self.code
                                    )
