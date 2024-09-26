from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import datetime
import json
from meeting_action import serializers as meeting_action_serializers
from meeting_action import models as meeting_action_models
from lib.permission import Action, PermissionManager, Module
from lib.response.type import ResponseType
from lib import constant
from Activity_log import views as activity_log_views


class MeetingScoreCreate(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 23 jan 2024
    purpose : meeting create
    url : /api/meeting/score/create
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MEETING
    action = Action.ADD

    meeting_score_main_serializer = meeting_action_serializers.MeetingScoreMainCreateSerializer
    meeting_score_indicator_serializer = meeting_action_serializers.MeetingScoreIndicatorCreate
    action_serializers = meeting_action_serializers.ActionSerializer

    def validation(self, uuid):
        try:
            sub_meeting_instance = meeting_action_models.SubMeeting.objects.get(uuid=uuid, deleted_at=None)
            if sub_meeting_instance.meeting_status == constant.COMPLETED:
                return {"error": True,
                        "message": "meeting status already completed"}
            if sub_meeting_instance.meeting_level == constant.INTERFACE_LEVEL:
                sub_meeting_for_meeting_lvl_check = meeting_action_models.SubMeeting.objects.filter(
                    schedule=sub_meeting_instance.schedule, meeting_status=constant.COMPLETED
                )
                if len(sub_meeting_for_meeting_lvl_check) != 2:
                    return {"error": True,
                            "message": "you have to complete community and service provider level meeting first"}
                else:
                    return {"error": False,
                            "message": ""}
            else:
                return {"error": False}

        except:
            return {"error": True, "message": "no meeting available with this uuid"}

    def post(self, request):
        data = request.data.copy()
        print(data)
        val = self.validation(data['meeting'])
        if val['error']:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: val['message'],
                ResponseType.DATA: data['uuid']
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            meeting_action_models.MeetingScoreMain.objects.get(
                deleted_at=None, uuid=data['uuid']
            )
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "meeting score already submitted",
                ResponseType.DATA: data['uuid']
            }, status=status.HTTP_400_BAD_REQUEST)
        except:
            pass

        try:
            sub_meeting_instance = meeting_action_models.SubMeeting.objects.get(
                deleted_at=None, uuid=data['meeting']
            )
        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "meeting not exists",
                ResponseType.DATA: data['uuid']
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            try:
                meeting_action_models.MeetingScoreMain.objects.get(deleted_at=None, uuid=data["uuid"])
                return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: "meeting score uuid already exists",
                    ResponseType.DATA: data["uuid"]
                }, status=status.HTTP_400_BAD_REQUEST)
            except:
                pass
            main_serializer = self.meeting_score_main_serializer(data={
                "meeting": sub_meeting_instance.id,
                "uuid": data["uuid"],
                "male": data["male"],
                "female": data["female"],
                "score_card_image": request.FILES['score_card_image'],
                "attendance_sheet_image": request.FILES['attendance_sheet_image'],
                "meeting_participant_image": request.FILES['meeting_participant_image'],
            })
            if main_serializer.is_valid(raise_exception=True):
                try:
                    activity_log_views.create_log(request.user, "submitted meeting score")
                except Exception as err:
                    print(str(err))
                main_serializer.save(created_by=request.user)
            else:
                return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: str(main_serializer.errors),
                    ResponseType.DATA: data['uuid']
                }, status=status.HTTP_400_BAD_REQUEST)

            indicator_flag = False
            for indicator in json.loads(data['indicator_list']):
                indicator_serializer = self.meeting_score_indicator_serializer(data={
                    "main": main_serializer.data["id"],
                    "indicator": indicator["id"],
                    "issue_against_indicator": indicator["issue_against_indicator"],
                    "reason_for_scoring": indicator["reason_for_scoring"],
                    "suggestion": indicator["suggestion"],
                    "score": indicator["score"],
                })
                if indicator_serializer.is_valid(raise_exception=True):
                    indicator_flag = True
                    indicator_serializer.save(created_by=request.user)
                else:
                    return Response({
                        ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                        ResponseType.MESSAGE: indicator_serializer.data,
                        ResponseType.DATA: data['uuid']
                    }, status=status.HTTP_400_BAD_REQUEST)

                if 'action_list' in indicator:
                    action_flag = False
                    for action in indicator['action_list']:
                        try:
                            meeting_action_models.Actions.objects.get(deleted_at=None, uuid=action['uuid'])
                            return Response({
                                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                ResponseType.MESSAGE: "action uuid already exists",
                                ResponseType.DATA: data["uuid"]
                            }, status=status.HTTP_400_BAD_REQUEST)
                        except:
                            pass
                        datetime_obj = datetime.fromtimestamp(action['datetime'])
                        formatted_datetime = datetime_obj.strftime('%Y-%m-%dT%H:%M:%S')

                        action['indicator'] = indicator["id"]
                        action['meeting'] = sub_meeting_instance.id
                        action['datetime'] = formatted_datetime
                        action['status'] = constant.IN_PROGRESS

                        act_serializer = self.action_serializers(data=action)
                        if act_serializer.is_valid(raise_exception=True):
                            action_flag = True
                            act_serializer.save(created_by=request.user, status='in_progress')
                        else:
                            return Response({
                                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                ResponseType.MESSAGE: act_serializer.errors,
                                ResponseType.DATA: action['uuid']
                            }, status=status.HTTP_400_BAD_REQUEST)

                    if action_flag:
                        try:
                            activity_log_views.create_log(request.user, "submitted action plan")
                        except Exception as err:
                            print(str(err))

            if indicator_flag:
                try:
                    activity_log_views.create_log(request.user, "submitted meeting score")
                except Exception as err:
                    print(str(err))

        try:
            try:
                activity_log_views.create_log(request.user, "submitted score")
            except Exception as err:
                print(str(err))

            sub_meeting_instance.meeting_status = constant.COMPLETED
            sub_meeting_instance.save()
            if sub_meeting_instance.meeting_level == constant.INTERFACE_LEVEL:
                parent_meeting_instance = sub_meeting_instance.schedule
                parent_meeting_instance.is_active = False
                parent_meeting_instance.save()

        except:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "error in meeting status update operation",
                ResponseType.DATA: data['uuid']
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            ResponseType.STATUS: status.HTTP_201_CREATED,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: data['uuid']
        }, status=status.HTTP_201_CREATED)


class MeetingScoreUpdate(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 23 jan 2024
    purpose : meeting create
    url : /api/meeting/score/update
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.MEETING
    action = Action.EDIT

    serializer_class = meeting_action_serializers.MeetingScoreIndicatorCreate

    def post(self, request):
        data = request.data.copy()
        try:
            meeting_score_instance = meeting_action_models.MeetingScoreIndicator.objects.get(
                deleted_at=None, id=data['id']
            )
            serializer = self.serializer_class(meeting_score_instance, data=data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_at=datetime.now(), updated_by=request.user)
                try:
                    activity_log_views.create_log(request.user, "updated meeting score")
                except Exception as err:
                    print(str(err))

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
        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(err),
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)


class MeetingListWithAllInfo(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 11 feb 2024
    purpose : meeting create
    url : /api/meeting/score/list
    """

    serializer_class = meeting_action_serializers.MeetingListWithAllInfoSerializer

    def get(self, request):
        try:
            uuid = request.GET.get('uuid')
            meeting_instances = meeting_action_models.SubMeeting.objects.get(
                deleted_at=None, uuid=uuid
            )
            serializer = self.serializer_class(meeting_instances, many=False)
            return Response({
                ResponseType.STATUS: status.HTTP_200_OK,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA: serializer.data
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "no meeting found with this uuid",
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)
