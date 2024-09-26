from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from Activity_log import models as activity_log_models
from Activity_log import serializers as activity_log_serializer
from lib.response.type import ResponseType
from lib.permission import Action, PermissionManager, Module
import uuid


def create_log(user, message):
    activity_log_models.ActivityLog.objects.create(user=user, message=message, uuid=str(uuid.uuid4()))


class ActivityLogListApi(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.ACTIVITY_LOG
    action = Action.READ

    serializer_class = activity_log_serializer.ActivityLogSerializer
    pagination_class = PageNumberPagination

    def get(self, request):
        search = request.GET.get('search')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        activity_instances = activity_log_models.ActivityLog.objects.filter(
            deleted_at=None
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['created_at__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['created_at__date__lte'] = to_date
        if search:
            activity_instances = activity_instances.filter(
                Q(user__userprofile__first_name__icontains=search) |
                Q(user__userrole__role__role_name__icontains=search)
            )
        activity_instances = activity_instances.filter(**filter_object)
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(activity_instances, request)
        serializer = self.serializer_class(paginated_queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)

        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": paginated_data.data["count"],
                "results": paginated_data.data["results"]
            }
        }, status=status.HTTP_200_OK)
