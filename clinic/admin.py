from django.contrib import admin
from clinic import models as clinic_model


admin.site.register(clinic_model.Clinic)
admin.site.register(clinic_model.ClinicLoc)
