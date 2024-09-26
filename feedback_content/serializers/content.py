from rest_framework import serializers
from feedback_content import models as feedback_content_models


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = feedback_content_models.Content
        fields = ['id', 'name', 'type', 'content_file', 'url', 'order', 'is_active', 'created_at']

    def to_representation(self, instance):
        data = super(ContentSerializer, self).to_representation(instance)
        data['created_at'] = instance.created_at.date()
        return data
