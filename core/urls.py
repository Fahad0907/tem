from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user-management/', include('user_management.urls', namespace='user_management')),
    path('api/location/', include('location.urls', namespace='location')),
    path('api/organization/', include('organization.urls', namespace='organization')),
    path('api/clinic/', include('clinic.urls', namespace='clinic')),
    path('api/otp/', include('otp.urls', namespace='otp')),
    path('api/meeting/', include('meeting_action.urls', namespace='meeting')),
    path('api/', include('feedback_content.urls', namespace='feedback_content')),
    path('api/dashboard/', include('Dashboard.urls', namespace='dashboard')),
    path('api/activity-log/', include('Activity_log.urls', namespace='Activity_log'))
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
