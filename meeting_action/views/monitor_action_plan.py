from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from meeting_action import models as meeting_action_models
from meeting_action import serializers as meeting_action_serializers
from lib.response.type import ResponseType
from lib.permission import Action, PermissionManager, Module
from lib import constant
from Activity_log import views as activity_log_views


class ActionPlanListMobileApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 7 jan 2024
    purpose : meeting create
    url : /api/meeting/action-plan/list/mobile
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MONITOR_ACTION_PLAN
    action = Action.READ
    serializer_class = meeting_action_serializers.ActionSerializer

    def post(self, request):
        data = request.data.copy()
        limit = data.get('limit', 10)
        filter_obj = {}
        if 'datetime' in data:
            filter_obj['datetime__gt'] = data['datetime']

        action_instances = meeting_action_models.Actions.objects.filter(
            deleted_at=None, **filter_obj
        )[:limit]
        serializer = self.serializer_class(action_instances, many=True)
        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: serializer.data
        })


class ActionPlanUpdate(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 7 jan 2024
    purpose : meeting create
    url : /api/meeting/action-plan/update
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MONITOR_ACTION_PLAN
    action = Action.EDIT
    serializer_class = meeting_action_serializers.ActionSerializer

    def post(self, request):
        data_list = request.data.copy()
        success_list = []
        error_list = []
        for data in data_list:
            try:
                action_instance = meeting_action_models.Actions.objects.get(deleted_at=None, uuid=data['uuid'])
            except:
                error_list.append({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: "no action found with this uuid",
                    ResponseType.DATA: data['uuid']
                })
                continue
            serializer = self.serializer_class(action_instance, data=data, partial=True)
            if serializer.is_valid():
                try:
                    activity_log_views.create_log(request.user, "updated action plan")
                except Exception as err:
                    print(str(err))

                serializer.save(updated_at=datetime.now(), updated_by=request.user)
                success_list.append({
                    ResponseType.STATUS: status.HTTP_200_OK,
                    ResponseType.MESSAGE: "success",
                    ResponseType.DATA: data['uuid']
                })
                continue
            else:
                error_list.append({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: serializer.errors,
                    ResponseType.DATA: data['uuid']
                })
        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "",
            ResponseType.DATA: {
                "success_list": success_list,
                "error_list": error_list
            }
        })


class ActinPlanListWithCommunityClinic(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 7 jan 2024
    purpose : meeting create
    url : /api/meeting/action-plan-clinic/list
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MONITOR_ACTION_PLAN
    action = Action.READ
    serializer_class = meeting_action_serializers.ActionSerializerListForClinic

    def post(self, request):
        data = request.data.copy()
        filter_obj = {}
        if 'datetime' in data:
            filter_obj['datetime__gt'] = data['datetime']
        limit = data.get('limit', 10)
        sub_meeting_instances = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, meeting_status=constant.COMPLETED, actions__isnull=False, **filter_obj
        ).distinct()[: limit]
        serializer = self.serializer_class(sub_meeting_instances, many=True)
        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: serializer.data
        }, status=status.HTTP_200_OK)


class MonitorActionPlanListApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 7 jan 2024
    purpose : meeting create
    url : /api/meeting/monitor-action-plan/list
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MONITOR_ACTION_PLAN
    action = Action.READ

    serializer_class = meeting_action_serializers.ActionSerializer
    pagination_class = PageNumberPagination

    def get(self, request):
        search = request.GET.get('search')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        action_instances = meeting_action_models.Actions.objects.filter(
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
            action_instances = action_instances.filter(
                Q(name__icontains=search) |
                Q(uuid__icontains=search)
            )
        action_instances = action_instances.filter(**filter_object)

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(action_instances, request)
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


class MonitorActionPlanDetailsApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 7 jan 2024
    purpose : meeting create
    url : /api/meeting/monitor-action-plan/details
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MONITOR_ACTION_PLAN
    action = Action.READ

    serializer_class = meeting_action_serializers.ActionSerializer

    def post(self, request):
        data = request.data.copy()
        try:
            action_instance = meeting_action_models.Actions.objects.get(
                deleted_at=None, id=data['id']
            )
            serializer = self.serializer_class(action_instance, many=False)
            return Response({
                ResponseType.STATUS: status.HTTP_200_OK,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA: serializer.data
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "No action found",
                ResponseType.DATA: {}
            })


class ActionPlanDeleteApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 7 jan 2024
    purpose : meeting create
    url : /api/meeting/action-plan/delete
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MONITOR_ACTION_PLAN
    action = Action.DELETE
    serializer_class = meeting_action_serializers.ActionSerializer

    def post(self, request):
        data = request.data.copy()
        try:
            action_instance = meeting_action_models.Actions.objects.get(
                deleted_at=None, id=data['id']
            )
            action_instance.deleted_at = datetime.now()
            action_instance.deleted_by = request.user
            action_instance.save()
            try:
                activity_log_views.create_log(request.user, "deleted action plan")
            except Exception as err:
                print(str(err))
            return Response({
                ResponseType.STATUS: status.HTTP_200_OK,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA: {}
            }, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(err),
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)


class ActionPlanUpdateWeb(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 7 jan 2024
    purpose : meeting update web
    url : /api/meeting/action-plan/update/web
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MONITOR_ACTION_PLAN
    action = Action.EDIT
    serializer_class = meeting_action_serializers.ActionSerializer

    def post(self, request):
        data = request.data.copy()
        try:
            action_instance = meeting_action_models.Actions.objects.get(deleted_at=None, id=data['id'])
            serializer = self.serializer_class(action_instance, data=data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user, updated_at=datetime.now())
                try:
                    activity_log_views.create_log(request.user, "updated action plan")
                except Exception as err:
                    print(str(err))
                return Response({
                    ResponseType.STATUS: status.HTTP_200_OK,
                    ResponseType.MESSAGE: "success",
                    ResponseType.DATA: {}
                })
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(serializer.errors),
                ResponseType.DATA: {}
            })
        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(err),
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)
