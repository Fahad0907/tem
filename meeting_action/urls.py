from django.urls import path
from meeting_action import views

app_name = 'meeting'

parent_meeting_url = [
    path('schedule/create', views.ParentMeetingCreateApi.as_view(), name='meeting_parent_create'),
    path('schedule/list', views.ParentMeetingListMobileApi.as_view(), name='meeting_parent_list'),
    path('schedule/list/web/<id>', views.ParentMeetingListWebApi.as_view(), name='meeting_parent_list_web'),
]

meeting_urlpatterns = [
    path('create', views.MeetingCreateApi.as_view(), name='meeting_create'),
    path('mobile/list', views.MeetingListMobileApi.as_view(), name='meeting_list_mobile'),
    path('list/web', views.MeetingListWebApi.as_view(), name='meeting_list_web'),
    path('list/three-types', views.ThreeTypesMeetingDetails.as_view(), name='meeting_list_three_types'),
    path('list/score/web/<id>', views.MeetingDetailsWithScore.as_view(), name='meeting_list_score_web'),
    path('delete', views.MeetingDeleteApi.as_view(), name='meeting_delete'),
    path('interface-level-meeting-validate', views.InterfaceLevelMeetingStartCheckingApi.as_view(),
         name='interface_level_meeting_validate')
]

indicator_urlpatterns = [
    path('indicator/list', views.IndicatorListApi.as_view(), name='meeting_indicator_list'),
    path('indicator/list/mobile', views.IndicatorMobileListApi.as_view(), name='meeting_indicator_list_mobile'),
    path('indicator/list/dropdown', views.IndicatorDropDown.as_view(), name='meeting_indicator_dropdown'),
    path('indicator/create', views.IndicatorCreateApi.as_view(), name='meeting_indicator_create'),
    path('indicator/delete', views.IndicatorDeleteApi.as_view(), name='meeting_indicator_delete'),
    path('indicator/update', views.IndicatorUpdateApi.as_view(), name='meeting_indicator_update'),
]

meeting_score_urlpatterns = [
    path('score/list', views.MeetingListWithAllInfo.as_view(), name='meeting_score_list'),
    path('score/create', views.MeetingScoreCreate.as_view(), name='meeting_score_create'),
    path('score/update', views.MeetingScoreUpdate.as_view(), name='meeting_score_update'),
]

meeting_action_plan = [
    path('action-plan/list/mobile', views.ActionPlanListMobileApi.as_view(), name='meeting_action_plan_list_mobile'),
    path('action-plan-community-clinic/list', views.ActinPlanListWithCommunityClinic.as_view(),
         name='meeting_action_plan_community_clinic_list'),
    path('action-plan/update', views.ActionPlanUpdate.as_view(), name='meeting_action_plan_update'),
    path('action-plan/update/web', views.ActionPlanUpdateWeb.as_view(), name='meeting_action_plan_update_web'),
    path('action-plan/delete', views.ActionPlanDeleteApi.as_view(), name='meeting_action_plan_delete'),
    path('monitor-action-plan/list', views.MonitorActionPlanListApi.as_view(), name='monitor_action_plan_list'),
    path('monitor-action-plan/details', views.MonitorActionPlanDetailsApi.as_view(), name='monitor_action_plan_details')
]


urlpatterns = (meeting_urlpatterns + parent_meeting_url + indicator_urlpatterns +
               meeting_score_urlpatterns + meeting_action_plan)
