from rest_framework.views import APIView
from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.utils import timezone
from meeting_action import serializers as meeting_action_serializers
from meeting_action import models as meeting_action_models
from user_management import models as user_management_model
from lib.permission import Action, PermissionManager, Module
from lib.response.type import ResponseType
from lib import constant
from Activity_log import views as activity_log_views
from datetime import datetime


class MeetingCreateApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 2 jan 2024
    purpose : meeting create
    url : /api/meeting/create
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MEETING
    action = Action.ADD
    serializer_class = meeting_action_serializers.MeetingSerializer

    def post(self, request):
        data_list = request.data.copy()
        success_list = []
        error_list = []
        for data in data_list:
            datetime_obj = datetime.fromtimestamp(data['datetime'])
            formatted_datetime = datetime_obj.strftime('%Y-%m-%dT%H:%M:%S')
            data['datetime'] = formatted_datetime

            sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(uuid=data['uuid'], deleted_at=None)
            if len(sub_meeting_instance):
                error_list.append({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: "Meeting with this uuid already exists",
                    ResponseType.DATA: data['uuid']
                })
                continue

            try:
                parent_meeting_instance = meeting_action_models.ParentMeeting.objects.get(
                    uuid=data['schedule']
                )
                data['schedule'] = parent_meeting_instance.id
            except Exception as err:
                print("error ######################")
                error_list.append({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: str(err),
                    ResponseType.DATA: data['uuid']
                })
                continue

            serializer = self.serializer_class(data=data, context={'request': request})
            if serializer.is_valid():
                try:
                    try:
                        activity_log_views.create_log(request.user, "created meeting")
                    except Exception as err:
                        print(str(err))

                    serializer.save()
                    success_list.append({
                        ResponseType.STATUS: status.HTTP_201_CREATED,
                        ResponseType.MESSAGE: "success",
                        ResponseType.DATA: serializer.data['uuid']
                    })
                    continue
                except serializers.ValidationError as err:
                    print("error in serializer ######################", str(err))
                    error_message = str(err.detail[0]) if err.detail else "Validation error occurred"
                    error_list.append({
                        ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                        ResponseType.MESSAGE: error_message,
                        ResponseType.DATA: data['uuid']
                    })
                    continue
            else:
                print("here")
                error_list.append({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: str(serializer.errors),
                    ResponseType.DATA: {}
                })
                continue

        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "",
            ResponseType.DATA: {
                "success_list": success_list,
                "error_list": error_list
            }
        }, status=status.HTTP_200_OK)


class InterfaceLevelMeetingStartCheckingApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 3 jan 2024
    purpose : check interface level meeting can be started or not
    url : /api/meeting/interface-level-meeting-validate
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MEETING
    action = Action.READ

    def post(self, request):
        data = request.data.copy()
        sub_meeting_instances = meeting_action_models.SubMeeting.objects.filter(
            schedule__uuid=data['schedule_uuid'], meeting_status='completed'
        )
        if len(sub_meeting_instances) < 2:
            return Response({"error": "you have to complete community and supervise level meeting"},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


class ParentMeetingCreateApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 2 jan 2024
    purpose : meeting create
    url : /api/meeting/parent/create
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MEETING
    action = Action.ADD
    serializer_class = meeting_action_serializers.ParentMeetingSerializer

    def post(self, request):
        data_list = request.data.copy()
        success_list = []
        error_list = []
        for data in data_list:
            parent_meeting_instance = meeting_action_models.ParentMeeting.objects.filter(
                Q(uuid=data['uuid']) | Q(name=data['name'])
            )
            if len(parent_meeting_instance):
                error_list.append({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: "Schedule already exists",
                    ResponseType.DATA: data['uuid']
                })
                continue

            datetime_obj = datetime.fromtimestamp(data['datetime'])
            formatted_datetime = datetime_obj.strftime('%Y-%m-%dT%H:%M:%S')
            data['datetime'] = formatted_datetime

            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                try:
                    activity_log_views.create_log(request.user, "created schedule")
                except Exception as err:
                    print(str(err))
                serializer.save(created_by=request.user, updated_by=request.user)
                success_list.append({
                    ResponseType.STATUS: status.HTTP_201_CREATED,
                    ResponseType.MESSAGE: "success",
                    ResponseType.DATA: serializer.data
                })
            else:
                error_list.append({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: str(serializer.errors),
                    ResponseType.DATA: data['uuid']
                })
        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "",
            ResponseType.DATA: {
                "success_list": success_list,
                "error_list": error_list
            }
        }, status=status.HTTP_200_OK)


class MeetingListMobileApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 9 jan 2024
    purpose : meeting list for mobile
    url : /api/meeting/mobile/list
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MEETING
    action = Action.READ
    serializer_class = meeting_action_serializers.MeetingListSerializer

    def post(self, request):
        data = request.data.copy()
        limit = data.get('limit', 10)
        try:
            clinic_list_by_login_user = user_management_model.UserClinic.objects.filter(
                user=request.user, deleted_at=None).values_list('clinic', flat=True)

            sub_meeting_instances = meeting_action_models.SubMeeting.objects.filter(
                schedule__community_clinic__id__in=clinic_list_by_login_user, deleted_at=None
            ).order_by('datetime')

            if 'datetime' in data:
                sub_meeting_instances = sub_meeting_instances.filter(datetime__gt=data['datetime'])
            sub_meeting_instances = sub_meeting_instances[:limit]
            serializer = self.serializer_class(sub_meeting_instances, many=True)
            return Response({
                ResponseType.STATUS: status.HTTP_200_OK,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA:  serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(err),
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)


class ParentMeetingListMobileApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 12 jan 2024
    purpose : meeting list for mobile
    url : /api/meeting/mobile/list
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MEETING
    action = Action.READ
    serializer_class = meeting_action_serializers.ParentMeetingSerializer

    def post(self, request):
        data = request.data.copy()
        search_dict = {}
        if 'datetime' in data:
            search_dict['datetime__gt'] = data['datetime']
        parent_meeting_instances = meeting_action_models.ParentMeeting.objects.filter(
            community_clinic__id__in=user_management_model.UserClinic.objects.filter(
                user=request.user
            ).values_list('clinic', flat=True), deleted_at=None, **search_dict, is_active=True
        ).order_by('datetime')
        serializer = self.serializer_class(parent_meeting_instances, many=True)
        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: serializer.data
        })


class MeetingListWebApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 29 feb 2024
    purpose : meeting list for web
    url : /api/meeting/list/web
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MEETING
    action = Action.READ

    serializer_class = meeting_action_serializers.MeetingListSerializer
    pagination_class = PageNumberPagination

    def get(self, request):
        search = request.GET.get('search')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        meeting_instances = meeting_action_models.SubMeeting.objects.filter(
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
            meeting_instances = meeting_instances.filter(
                Q(village_name__icontains=search) |
                Q(venue_name__icontains=search) |
                Q(uuid__icontains=search) |
                Q(schedule__community_clinic__name__icontains=search)
            )

        meeting_instances = meeting_instances.filter(**filter_object)

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(meeting_instances, request)
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


class MeetingDetailsWithScore(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MEETING
    action = Action.READ

    pagination_class = PageNumberPagination
    serializer_class = meeting_action_serializers.MeetingListWithScore

    def get(self, request, id):
        try:
            parent_meeting_instance = meeting_action_models.SubMeeting.objects.get(
                deleted_at=None, id=id
            )
            serializer = self.serializer_class(parent_meeting_instance, many=False, context={"meeting": id})
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


class MeetingDeleteApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 29 feb 2024
    purpose : meeting list for web
    url : /api/meeting/delete
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MEETING
    action = Action.DELETE

    def post(self, request):
        data = request.data.copy()
        try:
            sub_meeting_instance = meeting_action_models.SubMeeting.objects.get(
                deleted_at=None, id=data['id']
            )
            sub_meeting_instance.deleted_at = datetime.now()
            sub_meeting_instance.deleted_by = request.user
            sub_meeting_instance.save()
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


class ParentMeetingListWebApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 12 jan 2024
    purpose : schedule list for web
    url : /api/meeting/schedule/list/web
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MEETING
    action = Action.READ

    pagination_class = PageNumberPagination
    serializer_class = meeting_action_serializers.ParentMeetingSerializer

    def get(self, request, id):
        search = request.GET.get('search')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        parent_meeting_instances = meeting_action_models.ParentMeeting.objects.filter(
            community_clinic_id=id, deleted_at=None
        )
        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date
        if search:
            parent_meeting_instances = parent_meeting_instances.filter(
                Q(name__icontains=search) | Q(uuid__icontains=search)
            )
        parent_meeting_instances = parent_meeting_instances.filter(**filter_object)

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(parent_meeting_instances, request)
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


class ThreeTypesMeetingDetails(APIView):

    serializer_class = meeting_action_serializers.MeetingListWithAllInfoSerializer
    indicator_serializer = meeting_action_serializers.IndicatorWithMeeting

    def post(self, request):
        data = request.data.copy()
        data_obj = {}
        sub_meeting_instances = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id=data['id']
        )
        try:
            community_level_meeting_instance = sub_meeting_instances.get( meeting_level=constant.COMMUNITY_LEVEL)
            data_obj[constant.COMMUNITY_LEVEL] = self.serializer_class(
                community_level_meeting_instance, many=False
            ).data
        except:
            data_obj[constant.COMMUNITY_LEVEL] = {}

        try:
            service_provider_level_instance = sub_meeting_instances.get(meeting_level=constant.SERVICE_PROVIDER_LEVEL)
            data_obj[constant.SERVICE_PROVIDER_LEVEL] = self.serializer_class(
                service_provider_level_instance, many=False
            ).data
        except:
            data_obj[constant.SERVICE_PROVIDER_LEVEL] = {}

        try:
            interface_level_instance = sub_meeting_instances.get(meeting_level=constant.INTERFACE_LEVEL)
            data_obj[constant.INTERFACE_LEVEL] = self.serializer_class(
                interface_level_instance, many=False
            ).data
        except:
            data_obj[constant.INTERFACE_LEVEL] = {}

        indicator_instances = meeting_action_models.Indicator.objects.filter(deleted_at=None)
        ind_serializer = meeting_action_serializers.IndicatorWithMeeting(indicator_instances,
                                                                         many=True, context={"schedule_id": data["id"]})
        data_obj["indicators"] = ind_serializer.data

        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: data_obj
        }, status=status.HTTP_200_OK)
