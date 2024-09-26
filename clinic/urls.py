from django.urls import path
from clinic import views

app_name = 'clinic'

clinic_dropdown_urlpatterns = [
    path('list/dropdown', views.ClinicDropDownListApi.as_view(), name='list_dropdown'),
    path('list', views.ClinicListApi.as_view(), name='clinic_list'),
    path('details', views.ClinicDetailsApi.as_view(), name='clinic_details'),
    path('create', views.ClinicCreateApi.as_view(), name='clinic_create'),
    path('update', views.ClinicUpdateApi.as_view(), name='clinic_update'),
    path('update/all', views.ClinicUpdateAllApi.as_view(), name='clinic_update_all'),
    path('delete', views.ClinicDeleteApi.as_view(), name='clinic_delete')
]

urlpatterns = clinic_dropdown_urlpatterns
