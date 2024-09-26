from django.urls import path
from Dashboard import views

app_name = 'dashboard'

card_urlpatterns = [
    path('schedule-count', views.ScheduleCount.as_view(), name='schedule_count'),
    path('sub-meeting-total-count', views.TotalMeetingCount.as_view(), name='sub_meeting_total_count'),
    path('sub-meeting/community-level', views.TotalNumberOfCommunityLevelMeeting.as_view(), name='community_level'),
    path('sub-meeting/community-level/pending', views.TotalNumberOfPendingCommunityLevelMeeting.as_view(),
         name='community_level_pending'),
    path('sub-meeting/community-level/complete', views.TotalNumberOfCompleteCommunityLevelMeeting.as_view(),
         name='community_level_complete'),
    path('sub-meeting/community-level/expired', views.TotalNumberOfExpiredCommunityLevelMeeting.as_view(),
         name='community_level_expired'),
    path('sub-meeting/service-provider-level', views.TotalNumberOfServiceProviderLevelMeeting.as_view(),
         name='service_provider_level'),
    path('sub-meeting/service-provider-level/pending', views.TotalNumberOfPendingServiceProviderLevelMeeting.as_view(),
         name='service_provider_level_pending'),
    path('sub-meeting/service-provider-level/complete', views.TotalNumberOfCompleteServiceProviderLevelMeeting.as_view(),
         name='service_provider_level_complete'),
    path('sub-meeting/service-provider-level/expired', views.TotalNumberOfExpireServiceProviderLevelMeeting.as_view(),
         name='service_provider_level_expired'),
    path('sub-meeting/interface-level', views.TotalNumberOfInterfaceLevelMeeting.as_view(), name='interface_level'),
    path('sub-meeting/interface-level/pending', views.TotalNumberOfPendingInterfaceLevelMeeting.as_view(),
         name='interface_level_pending'),
    path('sub-meeting/interface-level/complete', views.TotalNumberOfCompleteInterfaceLevelMeeting.as_view(),
         name='interface_level_complete'),
    path('sub-meeting/interface-level/expired', views.TotalNumberOfExpiredInterfaceLevelMeeting.as_view(),
         name='interface_level_expired')
]

table_urlpatterns = [
    path('issues-against-indicator', views.IndicatorIssueTable.as_view(), name='issues_against_indicator'),
    path('action-against-indicator', views.ActionTable.as_view(), name='action_against_indicator')
]

urlpatterns = card_urlpatterns + table_urlpatterns
