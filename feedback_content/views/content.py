from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from lib.response.type import ResponseType
from lib.permission import Action, PermissionManager, Module
from feedback_content import models as feedback_content_models
from feedback_content import serializers as feedback_content_serializer
from Activity_log import views as activity_log_views


class ContentListApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 22 jan 2024
    purpose : content list show
    url : /api/content/list
    """
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [PermissionManager]
    # module = Module.CONTENT
    # action = Action.READ
    pagination_class = PageNumberPagination
    serializer_class = feedback_content_serializer.ContentSerializer

    def get(self, request):
        search = request.GET.get('search')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        content_instances = feedback_content_models.Content.objects.filter(
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
            content_instances = content_instances.filter(
                Q(name__icontains=search) | Q(type__icontains=search)
            )
        content_instances = content_instances.filter(**filter_object)

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(content_instances, request)
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


class ContentCreateApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 20 feb 2024
    purpose : content list show
    url : /api/content/create
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.CONTENT
    action = Action.ADD
    serializer_class = feedback_content_serializer.ContentSerializer

    def post(self, request):
        data = request.data.copy()
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            try:
                activity_log_views.create_log(request.user, "created content")
            except Exception as err:
                print(str(err))
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


class ContentListUpdateApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 22 jan 2024
    purpose : content list show
    url : /api/content/update
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.CONTENT
    action = Action.EDIT

    serializer_class = feedback_content_serializer.ContentSerializer

    def post(self, request):
        data = request.data.copy()
        try:
            content_instance = feedback_content_models.Content.objects.get(
                deleted_at=None, id=data['id']
            )
        except:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "No content found",
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(content_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_at=datetime.now(), updated_by=request.user)
            try:
                activity_log_views.create_log(request.user, "updated content")
            except Exception as err:
                print(str(err))
            return Response({
                ResponseType.STATUS: status.HTTP_200_OK,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA: {}
            }, status=status.HTTP_200_OK)
        return Response({
            ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
            ResponseType.MESSAGE: serializer.errors,
            ResponseType.DATA: {}
        }, status=status.HTTP_400_BAD_REQUEST)


class ContentDetailsApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 22 jan 2024
    purpose : content list show
    url : /api/content/update
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.CONTENT
    action = Action.EDIT
    serializer_class = feedback_content_serializer.ContentSerializer

    def post(self, request):
        data = request.data.copy()
        try:
            content_instance = feedback_content_models.Content.objects.get(
                id=data['id'], deleted_at=None
            )
            serializer = self.serializer_class(content_instance, many=False)
            return Response({
                ResponseType.STATUS: status.HTTP_200_OK,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA: serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(err),
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)


class ContentDeleteApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 22 feb 2024
    purpose : content list show
    url : /api/content/delete
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.CONTENT
    action = Action.DELETE

    def post(self, request):
        data = request.data.copy()
        try:
            content_instance = feedback_content_models.Content.objects.get(
                deleted_at=None, id=data['id']
            )
        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(err),
                ResponseType.DATA: {}
            }, status=status)

        content_instance.deleted_at = datetime.now()
        content_instance.deleted_by = request.user
        content_instance.save()
        try:
            activity_log_views.create_log(request.user, "deleted content")
        except Exception as err:
            print(str(err))

        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {}
        }, status=status.HTTP_200_OK)
