from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from clinic import models as clinic_models
from clinic import serializers as clinic_serializers
from location import models as location_model
from lib.response.type import ResponseType
from lib.permission import Action, PermissionManager, Module
from Activity_log import views as activity_log_views


class ClinicListApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 2 jan 2024
    purpose : clinic list show
    url : /api/clinic/list
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.CLINIC
    action = Action.READ

    serializer_class = clinic_serializers.ClinicSerializer
    pagination_class = PageNumberPagination

    def get(self, request):
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')
        search_value = request.GET.get('search')
        clinic_instances = clinic_models.Clinic.objects.filter(deleted_at=None)

        filter_object = {}
        if from_value:
            # Convert string to datetime object
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['created_at__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['created_at__date__lte'] = to_date
        if search_value:
            clinic_instances = clinic_instances.filter(Q(name__icontains=search_value) |
                                                       Q(email__icontains=search_value) |
                                                       Q(phone_number__icontains=search_value))

        clinic_instances = clinic_instances.filter(**filter_object).order_by("-id")

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(clinic_instances, request)
        serializer = self.serializer_class(paginated_queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)
        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": paginated_data.data["count"],
                "results": paginated_data.data["results"]
            }
        })


class ClinicDetailsApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 15 feb 2024
    purpose : clinic create
    url : /api/clinic/details
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.CLINIC
    action = Action.READ

    serializer_class = clinic_serializers.ClinicSerializer

    def post(self, request):
        try:
            data = request.data.copy()
            clinic_instance = clinic_models.Clinic.objects.get(
                deleted_at=None, id=data['id']
            )
            serializer = self.serializer_class(clinic_instance, many=False)
            return Response({
                ResponseType.STATUS: status.HTTP_200_OK,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA: serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(err),
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)


class ClinicCreateApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 15 feb 2024
    purpose : clinic create
    url : /api/clinic/create
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.CLINIC
    action = Action.ADD

    serializer_class = clinic_serializers.ClinicSerializer
    clinic_location_serializer_class = clinic_serializers.ClinicLocationSerializer

    def post(self, request):
        data = request.data.copy()
        main = data['main']
        try:
            clinic_instances = clinic_models.Clinic.objects.filter(
                (Q(name=main['name']) | Q(email=main['email']) | Q(phone_number=main['phone_number'])) & Q(deleted_at=None)
            )
            if len(clinic_instances):
                return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: "The clinic name, email or phone number already exists in the system.",
                    ResponseType.DATA: {}
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.serializer_class(data=data['main'])
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                location_instance = location_model.GeoData.objects.get(geocode=data['geocode'])
                loc_serializer = self.clinic_location_serializer_class(data={
                    "clinic": serializer.data['id'],
                    "location": location_instance.id
                })

                if loc_serializer.is_valid():
                    try:
                        activity_log_views.create_log(request.user, "created clinic")
                    except Exception as err:
                        print(str(err))

                    loc_serializer.save(created_by=request.user)
                    return Response({
                        ResponseType.STATUS: status.HTTP_201_CREATED,
                        ResponseType.MESSAGE: "success",
                        ResponseType.DATA: {}
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                        ResponseType.MESSAGE: loc_serializer.errors,
                        ResponseType.DATA: {}
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: serializer.errors,
                    ResponseType.DATA: {}
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(err),
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)


class ClinicUpdateApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 15 feb 2024
    purpose : clinic create
    url : /api/clinic/create
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.CLINIC
    action = Action.EDIT

    serializer_class = clinic_serializers.ClinicSerializer

    def post(self, request):
        data = request.data.copy()
        try:
            clinic_instance = clinic_models.Clinic.objects.get(
                deleted_at=None, id=data['id']
            )
        except:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "clinic not found",
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(clinic_instance, data=data, partial=True)
        if serializer.is_valid():
            try:
                activity_log_views.create_log(request.user, "updated clinic")
            except Exception as err:
                print(str(err))

            serializer.save(updated_by=request.user, updated_at=datetime.now())
            return Response({
                ResponseType.STATUS: status.HTTP_200_OK,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA: {}
            }, status=status.HTTP_200_OK)
        return Response({
            ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
            ResponseType.MESSAGE: serializer.errors,
            ResponseType.DATA: {}
        }, status=status.HTTP_400_BAD_REQUEST)


class ClinicUpdateAllApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 15 feb 2024
    purpose : clinic create
    url : /api/clinic/create
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.CLINIC
    action = Action.EDIT

    serializer_class = clinic_serializers.ClinicSerializer
    clinic_location_serializer = clinic_serializers.ClinicLocationSerializer

    def post(self, request):
        data = request.data.copy()
        main = data['main']
        filter_query = Q()
        if 'name' in main:
            filter_query |= Q(name=main['name'])
        if 'email' in main:
            filter_query |= Q(email=main['email'])
        if 'phone_number' in main:
            filter_query |= Q(phone_number=main['phone_number'])

        if filter_query:
            filter_query &= Q(deleted_at=None)
            clinic_instances = clinic_models.Clinic.objects.filter(filter_query)
        else:
            clinic_instances = clinic_models.Clinic.objects.none()

        if len(clinic_instances):
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "The clinic name, email or phone number already exists in the system.",
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            clinic_instance = clinic_models.Clinic.objects.get(
                deleted_at=None, id=data['id']
            )
        except:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "No Clinic found",
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(clinic_instance, data=data['main'], partial=True)
        if serializer.is_valid():
            try:
                activity_log_views.create_log(request.user, "updated clinic")
            except Exception as err:
                print(str(err))

            try:
                organization_loc_instance = clinic_models.ClinicLoc.objects.get(
                    deleted_at=None, clinic=clinic_instance
                )

                geodata_instance = location_model.GeoData.objects.get(
                    geocode=data['geocode']
                )

                organization_loc_instance.location_id = geodata_instance.id
                organization_loc_instance.save()
                serializer.save(updated_at=datetime.now(), updated_by=request.user)
                return Response({
                    ResponseType.STATUS: status.HTTP_200_OK,
                    ResponseType.MESSAGE: "success",
                    ResponseType.DATA: {}
                }, status=status.HTTP_200_OK)
            except Exception as err:
                return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: str(err),
                    ResponseType.DATA: {}
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: serializer.errors,
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)


class ClinicDeleteApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 15 feb 2024
    purpose : clinic create
    url : /api/clinic/create
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.CLINIC
    action = Action.DELETE

    def post(self, request):
        try:
            data = request.data.copy()
            clinic_instance = clinic_models.Clinic.objects.get(
                deleted_at=None, id=data['id']
            )

            try:
                activity_log_views.create_log(request.user, "deleted clinic")
            except Exception as err:
                print(str(err))

            clinic_instance.deleted_at = datetime.now()
            clinic_instance.deleted_by = request.user
            clinic_instance.save()

            return Response({
                ResponseType.STATUS: status.HTTP_200_OK,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA: {}
            }, status=status.HTTP_200_OK)

        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(err),
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)


