from rest_framework import serializers
from meeting_action import models as meeting_action_models
from meeting_action import serializers as meeting_action_serializers


class MeetingScoreMainCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = meeting_action_models.MeetingScoreMain
        fields = ['id', 'meeting', 'male', 'female', 'uuid',
                  'score_card_image', 'attendance_sheet_image', 'meeting_participant_image']

        extra_kwargs = {
            'uuid': {'required': True},
            'male': {'required': True},
            'female': {'required': True},
            'score_card_image': {'required': True},
            'attendance_sheet_image': {'required': True},
            'meeting_participant_image': {'required': True},
        }


class MeetingScoreIndicatorCreate(serializers.ModelSerializer):
    class Meta:
        model = meeting_action_models.MeetingScoreIndicator
        fields = ['id', 'main', 'indicator', 'issue_against_indicator', 'reason_for_scoring', 'suggestion', 'score']

        extra_kwargs = {
            'main': {'required': True},
            'indicator': {'required': True},
            'issue_against_indicator': {'required': True},
            'reason_for_scoring': {'required': True},
            'suggestion': {'required': True},
            'score': {'required': True},
        }


class MeetingScoreIndicatorList(serializers.ModelSerializer):
    class Meta:
        model = meeting_action_models.MeetingScoreIndicator
        fields = ['id', 'main', 'indicator', 'issue_against_indicator', 'reason_for_scoring', 'suggestion', 'score']

    def to_representation(self, instance):
        data = super(MeetingScoreIndicatorList, self).to_representation(instance)
        try:
            indicator_instance = meeting_action_models.Indicator.objects.get(
                deleted_at=None, is_active=True, id=instance.indicator.id
            )
            action_instances = meeting_action_models.Actions.objects.filter(
                deleted_at=None, meeting_id=self.context.get('meeting'), indicator=indicator_instance
            )
            data['indicator'] = {
                "id": indicator_instance.id,
                "name": indicator_instance.name,
                "action_list": meeting_action_serializers.ActionSerializer(action_instances, many=True).data
            }
            return data
        except:
            return data
