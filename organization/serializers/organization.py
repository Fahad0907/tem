from rest_framework import serializers
from organization import models as organization_model
from location import models as location_models
from user_management import models as user_management_models


class OrganizationDropDownSerializer(serializers.ModelSerializer):
    class Meta:
        model = organization_model.Organization
        fields = ['id', 'name']


class OrganizationSerializer(serializers.ModelSerializer):
    location_obj = serializers.SerializerMethodField(read_only=True)
    total_user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = organization_model.Organization
        fields = ['id', 'name', 'email', 'phone_number', 'location_obj', 'total_user']

    def get_location_obj(self, obj):
        try:
            location_instances = organization_model.OrganizationLoc.objects.get(
                deleted_at=None, organization=obj.id
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

    def get_total_user(self, obj):
        user_location_instances = user_management_models.UserOrganization.objects.filter(
            deleted_at=None, organization=obj.id
        )
        return user_location_instances.count()


class OrganizationLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = organization_model.OrganizationLoc
        fields = ['id', 'organization', 'location']
