from rest_framework import serializers
from clinic import models as clinic_models
from location import models as location_models
from user_management import models as user_management_models


class ClinicDropDownSerializer(serializers.ModelSerializer):
    class Meta:
        model = clinic_models.Clinic
        fields = ['id', 'name']


class ClinicSerializer(serializers.ModelSerializer):
    location_obj = serializers.SerializerMethodField(read_only=True)
    total_user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = clinic_models.Clinic
        fields = ['id', 'name', 'location_obj', 'phone_number', 'email', 'is_active', 'total_user']

    def get_location_obj(self, obj):
        try:
            location_instances = clinic_models.ClinicLoc.objects.get(
                deleted_at=None, clinic=obj.id
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
        user_clinic_instances = user_management_models.UserClinic.objects.filter(
            deleted_at=None, clinic=obj.id, user__is_active=True
        )
        return user_clinic_instances.count()


class ClinicLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = clinic_models.ClinicLoc
        fields = ['id', 'clinic', 'location']
