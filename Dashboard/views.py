from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import datetime
from lib.permission import Action, PermissionManager, Module
from lib.response.type import ResponseType
from lib import constant
from location import models as location_models
from clinic import models as clinic_models
from meeting_action import models as meeting_action_models
from meeting_action import serializers as meeting_action_serializer


class ScheduleCount(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.DASHBOARD
    action = Action.READ

    def get(self, request):
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list('id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list('clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        # main part
        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date

        schedule_instance = schedule_instance.filter(**filter_object)

        return Response({
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": schedule_instance.count()
            },
            ResponseType.STATUS: status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class TotalMeetingCount(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.DASHBOARD
    action = Action.READ

    def get(self, request):
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        print(cluster, division, district, sub_district, union, from_value, to_value, "============vv====")
        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id__in=schedule_instance
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date

        sub_meeting_instance = sub_meeting_instance.filter(
            **filter_object
        )

        return Response({
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": sub_meeting_instance.count()
            },
            ResponseType.STATUS: status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class TotalNumberOfCommunityLevelMeeting(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.DASHBOARD
    action = Action.READ

    def get(self, request):
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        print(cluster, division, district, sub_district, union, from_value, to_value, "============vv====")
        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id__in=schedule_instance, meeting_level=constant.COMMUNITY_LEVEL
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date

        sub_meeting_instance = sub_meeting_instance.filter(
            **filter_object
        )

        return Response({
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": sub_meeting_instance.count()
            },
            ResponseType.STATUS: status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class TotalNumberOfPendingCommunityLevelMeeting(APIView):
    def get(self, request):
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id__in=schedule_instance, meeting_level=constant.COMMUNITY_LEVEL,
            meeting_status=constant.PENDING
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date

        sub_meeting_instance = sub_meeting_instance.filter(
            **filter_object
        )

        return Response({
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": sub_meeting_instance.count()
            },
            ResponseType.STATUS: status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class TotalNumberOfCompleteCommunityLevelMeeting(APIView):
    def get(self, request):
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        today_date = timezone.localdate()
        print(today_date, '==============')
        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id__in=schedule_instance, meeting_level=constant.COMMUNITY_LEVEL,
            meeting_status=constant.COMPLETED, datetime__lte=today_date
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date

        sub_meeting_instance = sub_meeting_instance.filter(
            **filter_object
        )

        return Response({
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": sub_meeting_instance.count()
            },
            ResponseType.STATUS: status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class TotalNumberOfExpiredCommunityLevelMeeting(APIView):
    def get(self, request):
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        print(schedule_instance, "===================================")

        today_date = timezone.localdate()

        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id__in=schedule_instance, meeting_level=constant.COMMUNITY_LEVEL,
            meeting_status=constant.COMPLETED, datetime__gt=today_date
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date

        sub_meeting_instance = sub_meeting_instance.filter(
            **filter_object
        )

        return Response({
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": sub_meeting_instance.count()
            },
            ResponseType.STATUS: status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class TotalNumberOfServiceProviderLevelMeeting(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.DASHBOARD
    action = Action.READ

    def get(self, request):
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        print(cluster, division, district, sub_district, union, from_value, to_value, "============vv====")
        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id__in=schedule_instance, meeting_level=constant.SERVICE_PROVIDER_LEVEL
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date

        sub_meeting_instance = sub_meeting_instance.filter(
            **filter_object
        )

        return Response({
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": sub_meeting_instance.count()
            },
            ResponseType.STATUS: status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class TotalNumberOfPendingServiceProviderLevelMeeting(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.DASHBOARD
    action = Action.READ

    def get(self, request):
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        print(cluster, division, district, sub_district, union, from_value, to_value, "============vv====")
        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id__in=schedule_instance, meeting_level=constant.SERVICE_PROVIDER_LEVEL,
            meeting_status=constant.PENDING
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date

        sub_meeting_instance = sub_meeting_instance.filter(
            **filter_object
        )

        return Response({
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": sub_meeting_instance.count()
            },
            ResponseType.STATUS: status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class TotalNumberOfCompleteServiceProviderLevelMeeting(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.DASHBOARD
    action = Action.READ

    def get(self, request):
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        print(cluster, division, district, sub_district, union, from_value, to_value, "============vv====")
        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        today_date = timezone.localdate()

        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id__in=schedule_instance, meeting_level=constant.SERVICE_PROVIDER_LEVEL,
            meeting_status=constant.COMPLETED, datetime__lte=today_date
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date

        sub_meeting_instance = sub_meeting_instance.filter(
            **filter_object
        )

        return Response({
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": sub_meeting_instance.count()
            },
            ResponseType.STATUS: status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class TotalNumberOfExpireServiceProviderLevelMeeting(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.DASHBOARD
    action = Action.READ

    def get(self, request):
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        print(cluster, division, district, sub_district, union, from_value, to_value, "============vv====")
        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        today_date = timezone.localdate()

        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id__in=schedule_instance, meeting_level=constant.SERVICE_PROVIDER_LEVEL,
            meeting_status=constant.COMPLETED, datetime__gt=today_date
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date

        sub_meeting_instance = sub_meeting_instance.filter(
            **filter_object
        )

        return Response({
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": sub_meeting_instance.count()
            },
            ResponseType.STATUS: status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class TotalNumberOfInterfaceLevelMeeting(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.DASHBOARD
    action = Action.READ

    def get(self, request):
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        print(cluster, division, district, sub_district, union, from_value, to_value, "============vv====")
        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id__in=schedule_instance, meeting_level=constant.INTERFACE_LEVEL
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date

        sub_meeting_instance = sub_meeting_instance.filter(
            **filter_object
        )

        return Response({
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": sub_meeting_instance.count()
            },
            ResponseType.STATUS: status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class TotalNumberOfPendingInterfaceLevelMeeting(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.DASHBOARD
    action = Action.READ

    def get(self, request):
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        print(cluster, division, district, sub_district, union, from_value, to_value, "============vv====")
        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id__in=schedule_instance, meeting_level=constant.INTERFACE_LEVEL,
            meeting_status=constant.PENDING
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date

        sub_meeting_instance = sub_meeting_instance.filter(
            **filter_object
        )

        return Response({
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": sub_meeting_instance.count()
            },
            ResponseType.STATUS: status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class TotalNumberOfCompleteInterfaceLevelMeeting(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.DASHBOARD
    action = Action.READ

    def get(self, request):
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        print(cluster, division, district, sub_district, union, from_value, to_value, "============vv====")
        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        today_date = timezone.localdate()

        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id__in=schedule_instance, meeting_level=constant.INTERFACE_LEVEL,
            meeting_status=constant.COMPLETED, datetime__lte=today_date
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date

        sub_meeting_instance = sub_meeting_instance.filter(
            **filter_object
        )

        return Response({
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": sub_meeting_instance.count()
            },
            ResponseType.STATUS: status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class TotalNumberOfExpiredInterfaceLevelMeeting(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.DASHBOARD
    action = Action.READ

    def get(self, request):
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        print(cluster, division, district, sub_district, union, from_value, to_value, "============vv====")
        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        today_date = timezone.localdate()

        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id__in=schedule_instance, meeting_level=constant.INTERFACE_LEVEL,
            meeting_status=constant.COMPLETED, datetime__gt=today_date
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['datetime__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['datetime__date__lte'] = to_date

        sub_meeting_instance = sub_meeting_instance.filter(
            **filter_object
        )

        return Response({
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": sub_meeting_instance.count()
            },
            ResponseType.STATUS: status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class IndicatorIssueTable(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.DASHBOARD
    action = Action.READ

    pagination_class = PageNumberPagination
    serializer_class = meeting_action_serializer.IndicatorSerializerForDashboard

    def get(self, request):
        indicator_id = request.GET.get('indicatorId')
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, schedule_id__in=schedule_instance
        ).values_list('id')

        indicator_instances = meeting_action_models.MeetingScoreIndicator.objects.filter(
            indicator__id=indicator_id, main__meeting__id__in=sub_meeting_instance
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['created_at__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['created_at__date__lte'] = to_date

        indicator_instances = indicator_instances.filter(**filter_object)

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(indicator_instances, request)
        serializer = self.serializer_class(paginated_queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)

        return Response({
            "status": status.HTTP_200_OK,
            "data": {
                "count": paginated_data.data["count"],
                "results": paginated_data.data["results"]
            },
            "message": "success"
        }, status=status.HTTP_200_OK)


class ActionTable(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.DASHBOARD
    action = Action.READ

    pagination_class = PageNumberPagination
    serializer_class = meeting_action_serializer.ActionSerializerWithLocation

    def get(self, request):
        indicator_id = request.GET.get('indicatorId')
        cluster = request.GET.get('cluster')
        division = request.GET.get('division')
        district = request.GET.get('district')
        sub_district = request.GET.get('sub_district')
        union = request.GET.get('union')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        union_id = ()
        if cluster:
            district_id = location_models.GeoData.objects.filter(field_parent_id=cluster).values_list('id')
            upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
            union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')

        if division:
            try:
                division_instance = location_models.GeoData.objects.get(geocode=division)
                district_id = location_models.GeoData.objects.filter(field_parent_id=division_instance.id).values_list(
                    'id')
                upazila_id = location_models.GeoData.objects.filter(field_parent_id__in=district_id).values_list('id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("division not found")
                union_id = ()

        if district:
            try:
                district_instance = location_models.GeoData.objects.get(geocode=district)
                upazila_id = location_models.GeoData.objects.filter(field_parent_id=district_instance.id).values_list(
                    'id')
                union_id = location_models.GeoData.objects.filter(field_parent_id__in=upazila_id).values_list('id')
            except:
                print("no district found")
                union_id = ()

        if sub_district:
            sub_district_instance = location_models.GeoData.objects.get(geocode=sub_district)
            union_id = location_models.GeoData.objects.filter(
                field_parent_id=sub_district_instance.id).values_list('id')

        if union:
            union_id = location_models.GeoData.objects.filter(geocode=union).values_list('id')

        if union_id:
            print(clinic_models.ClinicLoc.objects.filter(location_id__in=union_id), "=====cl=====")
            clinic_loc_instances = clinic_models.ClinicLoc.objects.filter(location_id__in=union_id).values_list(
                'clinic')
            clinic_instance = clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances).values_list('id')
            print(clinic_models.Clinic.objects.filter(
                deleted_at=None, id__in=clinic_loc_instances), "=====ci=====")
        else:
            clinic_instance = clinic_models.Clinic.objects.filter(deleted_at=None).values_list('id')

        schedule_instance = meeting_action_models.ParentMeeting.objects.filter(
            deleted_at=None, community_clinic_id__in=clinic_instance
        ).values_list('id')

        sub_meeting_instance = meeting_action_models.SubMeeting.objects.filter(
            deleted_at=None, meeting_level=constant.INTERFACE_LEVEL, schedule_id__in=schedule_instance
        ).values_list('id')

        action_instance = meeting_action_models.Actions.objects.filter(
            deleted_at=None, indicator_id=indicator_id, meeting__id__in=sub_meeting_instance
        )

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['created_at__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['created_at__date__lte'] = to_date

        action_instance = action_instance.filter(**filter_object)
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(action_instance, request)
        serializer = self.serializer_class(paginated_queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)

        return Response({
            "status": status.HTTP_200_OK,
            "data": {
                "count": paginated_data.data["count"],
                "results": paginated_data.data["results"]
            },
            "message": "success"
        }, status=status.HTTP_200_OK)
