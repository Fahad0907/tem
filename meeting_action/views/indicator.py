from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import datetime
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.utils import timezone
from meeting_action import models as meeting_action_model
from meeting_action import serializers as meeting_action_serializer
from lib.permission import Action, PermissionManager, Module
from lib.response.type import ResponseType
from Activity_log import views as activity_log_views


class IndicatorListApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 9 jan 2024
    purpose : indicator list
    url : /api/meeting/indicator/list
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.INDICATOR
    action = Action.READ

    serializer_class = meeting_action_serializer.IndicatorSerializer
    pagination_class = PageNumberPagination

    def get(self, request):
        search = request.GET.get('search')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')
        indicator_instances = meeting_action_model.Indicator.objects.filter(deleted_at=None, is_active=True)

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['created_at__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['created_at__date__lte'] = to_date
        if search:
            indicator_instances = indicator_instances.filter(
                Q(name__icontains=search)
            )
        indicator_instances = indicator_instances.filter(**filter_object)

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(indicator_instances, request)
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


class IndicatorDropDown(APIView):
    serializer_class = meeting_action_serializer.IndicatorSerializer

    def get(self, request):
        indicator_instances = meeting_action_model.Indicator.objects.filter(
            deleted_at=None
        )
        serializer = self.serializer_class(indicator_instances, many=True)
        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.DATA: serializer.data,
            ResponseType.MESSAGE: "success"
        }, status=status.HTTP_200_OK)


class IndicatorCreateApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 15 jan 2024
    purpose : indicator create
    url : /api/meeting/indicator/create
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.INDICATOR
    action = Action.ADD
    serializer_class = meeting_action_serializer.IndicatorSerializer

    def post(self, request):
        data = request.data.copy()
        indicator_instance = meeting_action_model.Indicator.objects.filter(
            deleted_at=None, name=data['name']
        )
        if len(indicator_instance):
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "Indicator already exist",
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            try:
                activity_log_views.create_log(request.user, "created indicator")
            except Exception as err:
                print(str(err))
            serializer.save(created_by=request.user)
            return Response({
                ResponseType.STATUS: status.HTTP_201_CREATED,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA: {}
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(serializer.errors),
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)


class IndicatorDeleteApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 15 jan 2024
    purpose : indicator delete
    url : /api/meeting/indicator/delete
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.INDICATOR
    action = Action.DELETE
    serializer_class = meeting_action_serializer.IndicatorSerializer

    def post(self, request):
        data = request.data.copy()
        try:
            indicator_instance = meeting_action_model.Indicator.objects.get(
                id=data['id'], deleted_at=None
            )
        except:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "Indicator not exist",
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            indicator_instance.deleted_at = datetime.now()
            indicator_instance.save()
            try:
                activity_log_views.create_log(request.user, "deleted indicator")
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


class IndicatorUpdateApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 15 jan 2024
    purpose : indicator delete
    url : /api/meeting/indicator/delete
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.INDICATOR
    action = Action.EDIT
    serializer_class = meeting_action_serializer.IndicatorSerializer

    def post(self, request):
        data = request.data.copy()
        try:
            indicator_instance = meeting_action_model.Indicator.objects.get(
                id=data['id'], deleted_at=None
            )
        except:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "Indicator not exist",
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(indicator_instance, data=data, partial=True)
        if serializer.is_valid():
            try:
                activity_log_views.create_log(request.user, "updated indicator")
            except Exception as err:
                print(str(err))

            serializer.save()
            return Response({
                ResponseType.STATUS: status.HTTP_200_OK,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA: {}
            }, status=status.HTTP_200_OK)
        return Response({
            ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
            ResponseType.MESSAGE: str(serializer.errors),
            ResponseType.DATA: {}
        }, status=status.HTTP_400_BAD_REQUEST)


class IndicatorMobileListApi(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.INDICATOR
    action = Action.READ

    serializer_class = meeting_action_serializer.IndicatorSerializer

    def get(self, request):
        indicator_instances = meeting_action_model.Indicator.objects.filter(deleted_at=None, is_active=True)
        serializer = self.serializer_class(indicator_instances, many=True)
        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: serializer.data
        }, status=status.HTTP_400_BAD_REQUEST)
