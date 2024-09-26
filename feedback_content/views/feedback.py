from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
import uuid
from feedback_content import serializers as feedback_content_serializer
from lib.permission import Action, PermissionManager, Module
from lib.response.type import ResponseType
from feedback_content import models as feedback_content_models
from Activity_log import views as activity_log_views


class FeedBackCreateView(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 2 jan 2024
    purpose : feedback create
    url : /api/feedback/create
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.FEEDBACK
    action = Action.ADD
    serializer_class = feedback_content_serializer.FeedbackSerializer

    def post(self, request):
        data_list = request.data.copy()
        print(data_list, "===================", request.user)
        error_list = []
        success_list = []
        for data in data_list:
            data['user'] = request.user.id
            feedback_instances = feedback_content_models.Feedback.objects.filter(
                uuid=data['uuid'], deleted_at=None
            )
            if len(feedback_instances):
                error_list.append({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: "uuid already exists",
                    ResponseType.DATA: data['uuid']
                })
                continue
            if 'reschedule' in data and data['reschedule']:
                print("===========")
                try:
                    activity_log_views.create_log(request.user, "requested to reschedule meeting")
                    print("==here==")
                except Exception as err:
                    print(str(err), "==================")
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                try:
                    activity_log_views.create_log(request.user, "submitted feedback")
                except Exception as err:
                    print(str(err))
                success_list.append({
                    ResponseType.STATUS: status.HTTP_201_CREATED,
                    ResponseType.MESSAGE: "success",
                    ResponseType.DATA: serializer.data['uuid']
                })
            else:
                error_list.append({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: str(serializer.errors),
                    ResponseType.DATA: {}
                })
        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "",
            ResponseType.DATA: {
                "success_list": success_list,
                "error_list": error_list
            }
        }, status=status.HTTP_200_OK)


class FeedbackListMobileApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 9 jan 2024
    purpose : feedback list
    url : /api/feedback/list/mobile
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.FEEDBACK
    action = Action.READ

    serializer_class = feedback_content_serializer.FeedbackSerializer

    def post(self, request):
        data = request.data.copy()
        filter_obj = {}
        if 'created_at' in data:
            filter_obj['created_at__gt'] = data['created_at']

        feed_back_instances = feedback_content_models.Feedback.objects.filter(
            deleted_at=None, is_replied=True, **filter_obj
        )
        serializer = self.serializer_class(feed_back_instances, many=True)

        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: serializer.data
        }, status=status.HTTP_200_OK)


class FeedBackListApi(APIView):
    """
   Dev: Fakhrul Islam Fahad
   Date: 20 jan 2024
   purpose : feedback list
   url : /api/feedback/list
   """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.FEEDBACK
    action = Action.READ

    pagination_class = PageNumberPagination
    serializer_class = feedback_content_serializer.FeedbackSerializer

    def get(self, request):
        search = request.GET.get('search')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        feed_back_instances = feedback_content_models.Feedback.objects.filter(
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
            feed_back_instances = feed_back_instances.filter(
                Q(feedback_topic__icontains=search) | Q(feedback_description__icontains=search)
            )
        feed_back_instances = feed_back_instances.filter(**filter_object)

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(feed_back_instances, request)
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


class FeedbackCreateWebApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 20 jan 2024
    purpose : feedback list
    url : /api/feedback/create/web
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.FEEDBACK
    action = Action.ADD

    serializer_class = feedback_content_serializer.FeedbackSerializer

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        data['uuid'] = str(uuid.uuid4())
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(is_replied=True, created_by=request.user)
            try:
                activity_log_views.create_log(request.user, "submitted feedback")
            except Exception as err:
                print(str(err))

            return Response({
                ResponseType.STATUS: status.HTTP_201_CREATED,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA: {}
            }, status=status.HTTP_201_CREATED)
        return Response({
            ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
            ResponseType.MESSAGE: serializer.errors,
            ResponseType.DATA: {}
        }, status=status.HTTP_400_BAD_REQUEST)


class FeedbackDeleteApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 20 jan 2024
    purpose : feedback list
    url : /api/feedback/delete
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.FEEDBACK
    action = Action.DELETE

    def post(self, request):
        data = request.data.copy()
        try:
            feedback_instance = feedback_content_models.Feedback.objects.get(
                deleted_at=None, id=data['id']
            )
        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(err),
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)

        feedback_instance.deleted_at = datetime.now()
        feedback_instance.deleted_by = request.user
        feedback_instance.save()

        try:
            activity_log_views.create_log(request.user, "deleted feedback")
        except Exception as err:
            print(str(err))

        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {}
        }, status=status.HTTP_200_OK)
