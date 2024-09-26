from django.urls import path
from Activity_log import views

app_name = 'Activity_log'

urlpatterns = [
    path('list', views.ActivityLogListApi.as_view(), name='activity_log_list')
]
