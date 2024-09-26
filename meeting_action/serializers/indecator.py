from rest_framework import serializers
from meeting_action import models as meeting_action_model
from django.utils import timezone
from lib import constant
from meeting_action import serializers as meeting_action_serializers
from location import models as location_models
from clinic import models as clinic_models


class IndicatorSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = meeting_action_model.Indicator
        fields = ['id', 'is_active', 'name', 'date', 'time']

    def get_date(self, obj):
        local_datetime = timezone.localtime(obj.created_at)
        return local_datetime.date()

    def get_time(self, obj):
        local_datetime = timezone.localtime(obj.created_at)
        return local_datetime.strftime("%I:%M:%S %p")


class IndicatorWithMeeting(serializers.ModelSerializer):
    score = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = meeting_action_model.Indicator
        fields = ['id', 'is_active', 'name', 'score']

    def get_score(self, obj):

        try:
            data_obj = {
                "COMMUNITY_LEVEL": {},
                "SERVICE_PROVIDER_LEVEL": {},
                "INTERFACE_LEVEL": {}
            }
            try:
                meeting_score_indicator_instance_cm = meeting_action_model.MeetingScoreIndicator.objects.get(
                    indicator=obj,
                    main__meeting__meeting_level=constant.COMMUNITY_LEVEL,
                    main__meeting__deleted_at=None,
                    main__meeting__schedule__id=self.context.get("schedule_id")
                )
                data_obj["COMMUNITY_LEVEL"] = {
                    "score": meeting_score_indicator_instance_cm.score,
                    "suggestion": meeting_score_indicator_instance_cm.suggestion,
                    "reason_for_scoring": meeting_score_indicator_instance_cm.reason_for_scoring
                }
            except:
                pass

            try:
                meeting_score_indicator_instance_sp = meeting_action_model.MeetingScoreIndicator.objects.get(
                    indicator=obj,
                    main__meeting__meeting_level=constant.SERVICE_PROVIDER_LEVEL,
                    main__meeting__deleted_at=None,
                    main__meeting__schedule__id=self.context.get("schedule_id")
                )
                data_obj["SERVICE_PROVIDER_LEVEL"] = {
                    "score": meeting_score_indicator_instance_sp.score,
                    "suggestion": meeting_score_indicator_instance_sp.suggestion,
                    "reason_for_scoring": meeting_score_indicator_instance_sp.reason_for_scoring
                }
            except:
                pass

            try:
                meeting_score_indicator_instance_il = meeting_action_model.MeetingScoreIndicator.objects.get(
                    indicator=obj,
                    main__meeting__meeting_level=constant.INTERFACE_LEVEL,
                    main__meeting__deleted_at=None,
                    main__meeting__schedule__id=self.context.get("schedule_id")
                )
                meeting = meeting_action_model.SubMeeting.objects.get(
                    deleted_at=None, schedule_id=self.context.get("schedule_id"),
                    meeting_level= constant.INTERFACE_LEVEL
                    )

                action_instances = meeting_action_model.Actions.objects.filter(
                    indicator=obj, meeting=meeting.id
                    )
                print(action_instances, '==========')
                print(meeting_action_serializers.ActionListSerializer(
                        action_instances, many=True
                    ).data)
                data_obj["INTERFACE_LEVEL"] = {
                    "score": meeting_score_indicator_instance_il.score,
                    "suggestion": meeting_score_indicator_instance_il.suggestion,
                    "reason_for_scoring": meeting_score_indicator_instance_il.reason_for_scoring,
                    "action_list": meeting_action_serializers.ActionListSerializer(
                        action_instances, many=True
                    ).data
                }
            except:
                pass

            return data_obj
        except Exception as err:
            print(str(err))
            return {}


class IndicatorSerializerForDashboard(serializers.ModelSerializer):
    clinic_name = serializers.SerializerMethodField(read_only=True)
    location_obj = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = meeting_action_model.MeetingScoreIndicator
        fields = ['id', 'indicator', 'issue_against_indicator', 'main', 'clinic_name', 'location_obj']

    def get_clinic_name(self, obj):
        try:
            return obj.main.meeting.schedule.community_clinic.name
        except:
            return ""

    def get_location_obj(self, obj):
        try:
            location_instances = clinic_models.ClinicLoc.objects.get(
                deleted_at=None, clinic=obj.main.meeting.schedule.community_clinic.id
            )

            union = location_models.GeoData.objects.get(geocode=location_instances.location.geocode)
            sub_district = location_models.GeoData.objects.get(id=union.field_parent.id)
            district = location_models.GeoData.objects.get(id=sub_district.field_parent.id)
            division = location_models.GeoData.objects.get(id=district.field_parent.id)

            return {
                "union": {
                    "id": union.id,
                    "field_name": union.field_name,
                    "geocode": union.geocode
                },
                "sub_district": {
                    "id": sub_district.id,
                    "field_name": sub_district.field_name,
                    "geocode": sub_district.geocode
                },
                "district": {
                    "id": district.id,
                    "field_name": district.field_name,
                    "geocode": district.geocode
                },
                "division": {
                    "id": division.id,
                    "field_name": division.field_name,
                    "geocode": division.geocode
                }

            }
        except:
            return {}
