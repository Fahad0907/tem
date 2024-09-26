from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from meeting_action import models as meeting_action_models
from meeting_action import serializers as meeting_action_serializers
from clinic import models as clinic_models
from lib import constant


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = meeting_action_models.SubMeeting
        fields = ['id', 'schedule', 'meeting_level', 'village_name', 'venue_name',
                  'datetime', 'uuid']

    def create(self, validate_data):
        meeting_instance_with_schedule = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule=validate_data["schedule"]
        )
        if len(meeting_instance_with_schedule) >= 3:
            raise serializers.ValidationError("you can not create anymore meeting with this schedule")

        if (validate_data['meeting_level'] == 'community_level' or
                validate_data['meeting_level'] == 'service_provider_level'):

            meeting_validation_instances = meeting_action_models.SubMeeting.objects.filter(
                meeting_level=validate_data['meeting_level'],
                schedule=validate_data['schedule'],
                deleted_at=None
            )

            if len(meeting_validation_instances):
                raise serializers.ValidationError("meeting already exists")

            try:
                with transaction.atomic():
                    return meeting_action_models.SubMeeting.objects.create(
                        schedule=validate_data['schedule'],
                        meeting_level=validate_data['meeting_level'],
                        village_name=validate_data['village_name'],
                        venue_name=validate_data['venue_name'],
                        meeting_status='pending',
                        uuid=validate_data['uuid'],
                        datetime=validate_data['datetime'],
                        created_by=self.context['request'].user,
                        updated_by=self.context['request'].user
                    )
            except Exception as err:
                raise serializers.ValidationError(str(err))
        else:
            meeting_validation_instances = meeting_action_models.SubMeeting.objects.filter(
                schedule=validate_data['schedule'], deleted_at=None
            )
            if len(meeting_validation_instances) < 2:
                raise serializers.ValidationError(
                    'you have to create community level and service provider level meeting first'
                )
            elif len(meeting_validation_instances) > 2:
                raise serializers.ValidationError(
                    'all level meeting already scheduled'
                )
            try:
                latest_entry_of_sub_meeting = meeting_action_models.SubMeeting.objects.order_by(
                    '-datetime'
                ).first()

                # if latest_entry_of_sub_meeting.datetime < validate_data['datetime']:
                #     raise serializers.ValidationError("date time should be greater")

                return meeting_action_models.SubMeeting.objects.create(
                    schedule=validate_data['schedule'],
                    meeting_level=validate_data['meeting_level'],
                    village_name=validate_data['village_name'],
                    venue_name=validate_data['venue_name'],
                    meeting_status="pending",
                    uuid=validate_data['uuid'],
                    datetime=validate_data['datetime'],
                    created_by=self.context['request'].user,
                    updated_by=self.context['request'].user
                )
            except Exception as err:
                raise serializers.ValidationError(str(err))


class ParentMeetingSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)
    completed_meeting = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = meeting_action_models.ParentMeeting
        fields = ['id', 'community_clinic', 'name', 'uuid', 'datetime', 'is_active', 'date', 'time',
                  'completed_meeting']

        extra_kwargs = {
            'datetime': {
                'required': True
            }
        }

    def get_completed_meeting(self, obj):
        parent_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule=obj, meeting_status=constant.COMPLETED
        )
        return len(parent_meeting_instance)

    def get_date(self, obj):
        local_datetime = timezone.localtime(obj.datetime)
        return local_datetime.date()

    def get_time(self, obj):
        local_datetime = timezone.localtime(obj.datetime)
        return local_datetime.strftime('%I:%M %p')

    def to_representation(self, instance):
        data = super(ParentMeetingSerializer, self).to_representation(instance)
        try:
            clinic_instance = clinic_models.Clinic.objects.get(
                id=instance.community_clinic.id, deleted_at=None
            )
            data['community_clinic'] = {
                "id": clinic_instance.id,
                "name": clinic_instance.name
            }
            return data
        except:
            return data


class MeetingListSerializer(serializers.ModelSerializer):
    schedule_obj = serializers.SerializerMethodField(read_only=True)
    date = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = meeting_action_models.SubMeeting
        fields = ['id', 'meeting_level', 'village_name',
                  'venue_name', 'meeting_status', 'datetime',
                  'uuid', 'created_at', 'updated_at', 'created_by', 'date', 'time', 'schedule_obj']

    def get_date(self, obj):
        local_datetime = timezone.localtime(obj.datetime)
        return local_datetime.date()

    def get_time(self, obj):
        local_datetime = timezone.localtime(obj.datetime)
        return local_datetime.time()

    def get_schedule_obj(self, obj):
        try:
            parent_meeting_instance = meeting_action_models.ParentMeeting.objects.get(
                id=obj.schedule.id, deleted_at=None
            )
            return ParentMeetingSerializer(parent_meeting_instance, many=False).data

        except:
            pass


class MeetingListWithAllInfoSerializer(serializers.ModelSerializer):
    meeting_data = serializers.SerializerMethodField(read_only=True)
    meeting_score_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = meeting_action_models.SubMeeting
        fields = ['meeting_data', 'meeting_score_info']

    def get_meeting_score_info(self, obj):
        try:
            meeting_score_main_instance = meeting_action_models.MeetingScoreMain.objects.get(
                deleted_at=None, meeting=obj
            )
            meeting_score_indicator_instances = meeting_action_models.MeetingScoreIndicator.objects.filter(
                deleted_at=None, main=meeting_score_main_instance
            )

            return {
                "uuid": meeting_score_main_instance.uuid,
                "male": meeting_score_main_instance.male,
                "female": meeting_score_main_instance.female,
                "score_card_image": meeting_score_main_instance.score_card_image.url,
                "attendance_sheet_image": meeting_score_main_instance.attendance_sheet_image.url,
                "meeting_participant_image": meeting_score_main_instance.meeting_participant_image.url,
                "indicator_list": meeting_action_serializers.MeetingScoreIndicatorList(
                    meeting_score_indicator_instances, many=True, context={"meeting": obj.id}
                ).data
            }
        except:
            {}

    def get_meeting_data(self, obj):
        return MeetingListSerializer(obj, many=False).data


class MeetingListWithScore(serializers.ModelSerializer):
    schedule_obj = serializers.SerializerMethodField(read_only=True)
    date = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)
    submission_obj = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = meeting_action_models.SubMeeting
        fields = ['id', 'meeting_level', 'village_name',
                  'venue_name', 'meeting_status', 'datetime',
                  'uuid', 'created_at', 'updated_at', 'created_by', 'date', 'time', 'schedule_obj', 'submission_obj']

    def get_date(self, obj):
        local_datetime = timezone.localtime(obj.datetime)
        return local_datetime.date()

    def get_time(self, obj):
        local_datetime = timezone.localtime(obj.created_at)
        return local_datetime.strftime('%I:%M %p')

    def get_schedule_obj(self, obj):
        try:
            parent_meeting_instance = meeting_action_models.ParentMeeting.objects.get(
                id=obj.schedule.id, deleted_at=None
            )
            return ParentMeetingSerializer(parent_meeting_instance, many=False).data

        except:
            pass

    def get_submission_obj(self, obj):
        try:
            meeting_score_main_instance = meeting_action_models.MeetingScoreMain.objects.get(
                meeting=obj, deleted_at=None
            )
            meeting_score_indicator_instance = meeting_action_models.MeetingScoreIndicator.objects.filter(
                main=meeting_score_main_instance, deleted_at=None
            )

            return {
                "main":
                    meeting_action_serializers.MeetingScoreMainCreateSerializer(
                        meeting_score_main_instance, many=False
                    ).data,
                "score": meeting_action_serializers.MeetingScoreIndicatorList(
                        meeting_score_indicator_instance, many=True, context={"meeting": self.context.get('meeting')}
                    ).data
            }
        except:
            return {}
