from rest_framework import serializers
from django.utils import timezone
from clinic import models as clinic_models
from meeting_action import models as meeting_action_models
from location import models as location_models


class ActionSerializer(serializers.ModelSerializer):

    clinic = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = meeting_action_models.Actions
        fields = ['id', 'meeting', 'indicator', 'uuid', 'name',
                  'comment', 'status', 'date_from', 'date_to',
                  'supervisor', 'organization', 'datetime', 'clinic'
                  ]
        extra_kwargs = {
            'date_from': {'required': True},
            'date_to': {'required': True},
            'uuid': {'required': True},
        }

    def to_representation(self, instance):
        data = super(ActionSerializer, self).to_representation(instance)

        try:
            meeting_instance = meeting_action_models.SubMeeting.objects.get(
                id=instance.meeting.id, deleted_at=None
            )

            data['meeting'] = {
                'id': meeting_instance.id,
                'uuid': meeting_instance.uuid
            }
            return data
        except:
            data

    def get_clinic(self, obj):
        try:
            schedule_instance = meeting_action_models.SubMeeting.objects.get(deleted_at=None, id=obj.meeting.id)
            return schedule_instance.schedule.community_clinic.name
        except:
            return {}


class ActionSerializerListForClinic(serializers.ModelSerializer):
    date = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)
    schedule_obj = serializers.SerializerMethodField(read_only=True)
    action_count = serializers.SerializerMethodField(read_only=True)
    action_list = serializers.SerializerMethodField(read_only=True)
    clinic_obj = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = meeting_action_models.SubMeeting
        fields = ['id', 'uuid', 'datetime', 'date', 'time', 'schedule_obj', 'action_count', 'action_list', 'clinic_obj']

    def get_clinic_obj(self, obj):
        try:
            schedule_instance = meeting_action_models.ParentMeeting.objects.get(id=obj.schedule.id)
            clinic_instance = clinic_models.Clinic.objects.get(id=schedule_instance.community_clinic.id)
            return {
                "id": clinic_instance.id,
                "name": clinic_instance.name,
                "email": clinic_instance.email,
                "phone": clinic_instance.phone_number
            }
        except:
            return {}

    def get_date(self, obj):
        local_datetime = timezone.localtime(obj.datetime)
        return local_datetime.date()

    def get_time(self, obj):
        local_datetime = timezone.localtime(obj.datetime)
        return local_datetime.strftime("%I:%M %p")

    def get_schedule_obj(self, obj):
        try:
            parent_meeting_instance = meeting_action_models.ParentMeeting.objects.get(
                    deleted_at=None, id=obj.schedule.id
            )
            return {
                "id": parent_meeting_instance.id,
                "uuid": parent_meeting_instance.uuid,
                "name": parent_meeting_instance.name
            }
        except:
            return {}

    def get_action_count(self, obj):
        action_instances = meeting_action_models.Actions.objects.filter(
            deleted_at=None, meeting=obj.id
        )
        return {
            "total": len(action_instances),
            "in_progress": len(action_instances.filter(status='in_progress')),
            "not_started": len(action_instances.filter(status='not_started')),
            "done": len(action_instances.filter(status='done')),
            "wont_do": len(action_instances.filter(status='wont_do')),
        }

    def get_action_list(self, obj):
        action_instance = meeting_action_models.Actions.objects.filter(
            deleted_at=None, meeting=obj.id
        )
        return ActionSerializer(action_instance, many=True).data


class ActionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = meeting_action_models.Actions
        fields = ['id', 'name', 'comment', 'status', 'datetime', 'date_from', 'date_to', 'supervisor', 'organization']


class ActionSerializerWithLocation(serializers.ModelSerializer):
    clinic = serializers.SerializerMethodField(read_only=True)
    location_obj = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = meeting_action_models.Actions
        fields = ['id', 'name', 'comment', 'status', 'clinic', 'location_obj']

    def get_clinic(self, obj):
        try:
            return obj.meeting.schedule.community_clinic.name
        except:
            return ""

    def get_location_obj(self, obj):
        try:
            location_instances = clinic_models.ClinicLoc.objects.get(
                deleted_at=None, clinic=obj.meeting.schedule.community_clinic.id
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

