from rest_framework import serializers
from django.utils import timezone
from user_management import models as user_management_model
from clinic import models as clinic_model
from clinic import serializers as clinic_serializer
from location import serializers as location_serializer
from location import models as location_models


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_management_model.User
        fields = ['id', 'username', 'password', 'is_active']

    def create(self, validated_data):
        user = user_management_model.User.objects.create_user(**validated_data)
        user.is_active = False
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_management_model.UserModuleProfile
        fields = ['id', 'user', 'first_name', 'email', 'gender', 'phone', 'picture']
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'phone': {'required': True, 'allow_blank': False},
            'gender': {'required': True, 'allow_blank': False},
        }


class UserDetailsSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    gender = serializers.SerializerMethodField(read_only=True)
    phone = serializers.SerializerMethodField(read_only=True)
    picture = serializers.SerializerMethodField(read_only=True)
    organization = serializers.SerializerMethodField(read_only=True)
    clinic = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    date = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)
    role = serializers.SerializerMethodField(read_only=True)
    role_obj = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = user_management_model.User
        fields = ['id', 'username', 'is_active', 'first_name', 'email', 'gender', 'phone', 'picture',
                  'organization', 'clinic', 'location', 'date', 'time', 'role', 'role_obj']

    def get_first_name(self, obj):
        return obj.userprofile.first_name

    def get_email(self, obj):
        return obj.userprofile.email

    def get_gender(self, obj):
        return obj.userprofile.gender

    def get_phone(self, obj):
        return obj.userprofile.phone

    def get_picture(self, obj):
        try:
            return obj.userprofile.picture.url
        except:
            return ""

    def get_organization(self, obj):
        try:
            a = user_management_model.UserOrganization.objects.get(user=obj)
            return {
                "name": a.organization.name,
                "id": a.organization_id
            }
        except:
            return {}

    def get_clinic(self, obj):
        try:
            clinic_instances = clinic_model.Clinic.objects.filter(
                id__in=user_management_model.UserClinic.objects.filter(user=obj).values_list('clinic', flat=True))
            return clinic_serializer.ClinicDropDownSerializer(clinic_instances, many=True).data
        except Exception as err:
            print(err, "==========")
            return ""

    def get_location(self, obj):
        user_location_instances = user_management_model.UserLoc.objects.filter(user=obj)

        data = {
            "Division": "",
            "District": "",
            "Upazila": "",
            "Union": ""
        }
        field_type = user_location_instances[0].location.field_type_id
        id = user_location_instances[0].location.id
        while field_type > 1:
            loc_instance = location_models.GeoData.objects.get(id=id)
            id = loc_instance.field_parent_id
            field_type = loc_instance.field_type_id
            data[location_models.GeoDefinition.objects.get(id=field_type).node_name] = {
                "field_name": loc_instance.field_name,
                "geocode": loc_instance.geocode
            }
        data['Union'] = [data['Union']]
        if len(user_location_instances):
            union_list = []
            for loc in user_location_instances:
                loc_instance = location_models.GeoData.objects.get(geocode=loc.location.geocode)
                union_list.append({
                    "geocode": loc_instance.geocode,
                    "field_name": loc_instance.field_name
                })
            data['Union'] = union_list
        return data

    def get_date(self, obj):
        local_datetime = timezone.localtime(obj.created_at)
        return local_datetime.date()

    def get_time(self, obj):
        local_datetime = timezone.localtime(obj.created_at)
        return local_datetime.strftime('%I:%M %p')

    def get_role(self, obj):
        try:
            role_instance = user_management_model.UserRole.objects.get(
                deleted_at=None, user=obj
            )
            return role_instance.role.role_name
        except:
            return ""

    def get_role_obj(self, obj):
        try:
            role_instance = user_management_model.UserRole.objects.get(
                deleted_at=None, user=obj
            )
            return {
                "name": role_instance.role.role_name,
                "id": role_instance.role.id
            }
        except:
            return {}
