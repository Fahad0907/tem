from django.urls import path
from otp import views

app_name = 'otp'

urlpatterns = [
    path('create', views.OtpCreateApi.as_view(), name='otp_create'),
    path('validate', views.OtpValidationApi.as_view(), name='otp_validate'),
]
