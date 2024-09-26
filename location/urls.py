from django.urls import path
from location import views

app_name = 'location'

urlpatterns = [
    path('list', views.LocationListApi.as_view(), name='list'),
    path('cluster/list', views.ClusterListApi.as_view(), name='cluster_list'),
    path('div', views.DivisionBaseOnCluster.as_view(), name='div'),
    path('upload', views.LocationUploadApi.as_view(), name='upload')
]
