from django.urls import path
from organization import views

app_name = 'organization'
organization_dropdown_urlpatterns = [
    path('list/dropdown', views.OrganizationListApiForDropDown.as_view(), name='list_dropdown'),
    path('list', views.OrganizationListApi.as_view(), name='organization_list'),
    path('create', views.OrganizationCreateApi.as_view(), name='organization_create'),
    path('details', views.OrganizationDetailsApi.as_view(), name='organization_details'),
    path('update', views.OrganizationUpdateApi.as_view(), name='organization_update'),
    path('delete', views.OrganizationDeleteApi.as_view(), name='organization_delete'),
]

urlpatterns = organization_dropdown_urlpatterns
