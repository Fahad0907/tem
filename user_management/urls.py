from django.urls import path, include
from user_management import views
from rest_framework_simplejwt.views import TokenRefreshView


app_name = 'user_management'

sign_in_urlpatterns = [
    path('signin', views.SignInApi.as_view(), name='signin'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh')
]

user_urlpatterns = [
    path('create-mobile', views.UserCreateMobileApi.as_view(), name='user_create'),
    path('create-web', views.UserCreateWebApi.as_view(), name='user_create_web'),
    path('short-details', views.UserShortDetailsApi.as_view(), name='user_short_details'),
    path('profile-picture-update', views.UserProfilePictureUpdateApi.as_view(), name='user_profile_picture_update'),
    path('password-reset', views.UserPasswordResetApi.as_view(), name='user_password_reset'),
    path('password-reset/email', views.UserPasswordUpdateByEmail.as_view(), name='user_password_reset_email'),
    path('list', views.UserListApi.as_view(), name='user_list'),
    path('update', views.UserEditApi.as_view(), name='user_update'),
    path('details', views.UserDetailsApi.as_view(), name='user_details'),
    path('delete', views.UserDeleteApi.as_view(), name='user_delete'),
    path('email-validation', views.UserEmailValidation.as_view(), name='user_email_validation')
]

role_urlpatterns = [
    path('role/list/drop-down', views.RoleListDropDown.as_view(), name='role_list_drop_down'),
    path('role/list', views.RoleList.as_view(), name='role_list')
]

permission_urlpatterns = [
    path('permission/list/<id>', views.PermissionList.as_view(), name='permission_list'),
    path('permission/update', views.PermissionUpdate.as_view(), name='permission_update')
]

pending_user_urlpatterns = [
    path('pending-user/list', views.PendingUserListApi.as_view(), name='pending_user_list'),
    path('pending-user/update', views.UserActiveApi.as_view(), name='pending_user_update'),
    path('pending-user/reject', views.UserRejectApi.as_view(), name='pending_user_reject'),
]

urlpatterns = sign_in_urlpatterns + user_urlpatterns + role_urlpatterns + permission_urlpatterns + \
              pending_user_urlpatterns
