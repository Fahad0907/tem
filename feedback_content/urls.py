from django.urls import path
from feedback_content import views

app_name = 'feedback_content'

content_urlpatterns = [
    path('content/list', views.ContentListApi.as_view(), name='content_list'),
    path('content/create', views.ContentCreateApi.as_view(), name='content_create'),
    path('content/details', views.ContentDetailsApi.as_view(), name='content_details'),
    path('content/update', views.ContentListUpdateApi.as_view(), name='content_update'),
    path('content/delete', views.ContentDeleteApi.as_view(), name='content_delete')
]

feedback_urlpatterns = [
    path('feedback/create', views.FeedBackCreateView.as_view(), name='feedback_create'),
    path('feedback/create/web', views.FeedbackCreateWebApi.as_view(), name='feedback_create_web'),
    path('feedback/list/mobile', views.FeedbackListMobileApi.as_view(), name='feedback_list_mobile'),
    path('feedback/list', views.FeedBackListApi.as_view(), name='feedback_list'),
    path('feedback/delete', views.FeedbackDeleteApi.as_view(), name='feedback_delete'),
]

urlpatterns = feedback_urlpatterns + content_urlpatterns
