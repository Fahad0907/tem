from rest_framework import serializers
from location import models as location_model


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = location_model.GeoData
        fields = ['id', 'field_name', 'field_type', 'geocode']

    def to_representation(self, instance):
        data = super(LocationSerializer, self).to_representation(instance)
        try:
            geo_definition_instance = location_model.GeoDefinition.objects.get(id=instance.field_type.id)
            data['field_type'] = {
                'id': geo_definition_instance.id,
                'name': geo_definition_instance.node_name
            }
            return data
        except:
            return data


class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = location_model.Cluster
        fields = ['id', 'name', 'loc']

    def to_representation(self, instance):
        data = super(ClusterSerializer, self).to_representation(instance)
        try:
            geo_definition_instance = location_model.GeoData.objects.get(id=instance.loc.id)
            print(geo_definition_instance)
            data['loc'] = {
                'id': geo_definition_instance.id,
                'name': geo_definition_instance.field_name
            }

            return data
        except:
            return data

