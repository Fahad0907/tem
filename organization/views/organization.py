from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from organization import serializers as organization_serializer
from organization import models as organization_models
from location import models as location_model
from lib.response.type import ResponseType
from lib.permission import Action, PermissionManager, Module
from Activity_log import views as activity_log_views


class OrganizationListApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 23 jan 2024
    purpose : meeting create
    url : /api/organization/list
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.ORGANIZATION
    action = Action.READ

    organization_serializer = organization_serializer.OrganizationSerializer
    pagination_class = PageNumberPagination

    def get(self, request):
        search = request.GET.get('search')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        filter_object = {}
        organization_instances = organization_models.Organization.objects.filter(deleted_at=None)
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['created_at__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['created_at__date__lte'] = to_date

        if search:
            organization_instances = organization_instances.filter(
                Q(name__icontains=search) | Q(email__icontains=search) | Q(phone_number__icontains=search)
            )
        organization_instances = organization_instances.filter(**filter_object).order_by('-id')
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(organization_instances, request)
        serializer = self.organization_serializer(paginated_queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)
        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": paginated_data.data["count"],
                "results": paginated_data.data["results"]
            }
        })


class OrganizationCreateApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 23 jan 2024
    purpose : meeting create
    url : /api/organization/create
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.ORGANIZATION
    action = Action.ADD

    serializer_class = organization_serializer.OrganizationSerializer
    organization_location_serializer_class = organization_serializer.OrganizationLocationSerializer

    def post(self, request):
        data = request.data.copy()
        try:
            organization_instances = organization_models.Organization.objects.filter(
                (Q(email=data['email']) | Q(phone_number=data['phone_number'])) & Q(deleted_at=None)
            )

            if len(organization_instances):
                return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: "The email or phone number already exists in the system.",
                    ResponseType.DATA: {}
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.serializer_class(data={
                "name": data['name'],
                "email": data['email'],
                "phone_number": data['phone_number']
            })
            if serializer.is_valid():
                try:
                    activity_log_views.create_log(request.user, "created organization")
                except Exception as err:
                    print(str(err))

                serializer.save(created_by=request.user)
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

        try:
            location_instance = location_model.GeoData.objects.get(geocode=data['geocode'])
            loc_serializer = self.organization_location_serializer_class(data={
                "organization": serializer.data['id'],
                "location": location_instance.id
            })
            if loc_serializer.is_valid():
                loc_serializer.save(created_by=request.user)
                return Response({
                    ResponseType.STATUS: status.HTTP_201_CREATED,
                    ResponseType.MESSAGE: "success",
                    ResponseType.DATA: {}
                }, status=status.HTTP_201_CREATED)

        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(err),
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)


class OrganizationDetailsApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 23 jan 2024
    purpose : meeting create
    url : /api/organization/create
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.ORGANIZATION
    action = Action.READ

    serializer_class = organization_serializer.OrganizationSerializer

    def post(self, request):
        data = request.data.copy()
        try:
            organization_instance = organization_models.Organization.objects.get(
                deleted_at=None, id=data['id']
            )
            serializer = self.serializer_class(organization_instance, many=False)
            return Response({
                ResponseType.STATUS: status.HTTP_200_OK,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA: serializer.data
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "No organization found",
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)


class OrganizationUpdateApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 23 jan 2024
    purpose : meeting create
    url : /api/organization/update
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.ORGANIZATION
    action = Action.EDIT

    serializer_class = organization_serializer.OrganizationSerializer

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
            organization_instances = organization_models.Organization.objects.filter(filter_query)
        else:
            organization_instances = organization_models.Organization.objects.none()

        if len(organization_instances):
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "Email or phone number should be unique",
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            organization_instance = organization_models.Organization.objects.get(
                deleted_at=None, id=data['id']
            )
        except:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "No organization found",
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(organization_instance, data=data['main'], partial=True)
        if serializer.is_valid():
            try:
                organization_loc_instance = organization_models.OrganizationLoc.objects.get(
                    deleted_at=None, organization=organization_instance
                )

                geodata_instance = location_model.GeoData.objects.get(
                    geocode=data['geocode']
                )

                organization_loc_instance.location_id = geodata_instance.id
                organization_loc_instance.save()
                serializer.save(updated_at=datetime.now(), updated_by=request.user)

                try:
                    activity_log_views.create_log(request.user, "organization updated")
                except Exception as err:
                    print(str(err))

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


class OrganizationDeleteApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 23 jan 2024
    purpose : meeting delete
    url : /api/organization/delete
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.ORGANIZATION
    action = Action.DELETE

    serializer_class = organization_serializer.OrganizationSerializer

    def post(self, request):
        data = request.data.copy()
        try:
            organization_instance = organization_models.Organization.objects.get(
                id=data['id'], deleted_at=None
            )
        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "No Organization found",
                ResponseType.DATA: {}
            })

        organization_instance.deleted_at = datetime.now()
        organization_instance.deleted_by = request.user
        organization_instance.save()

        try:
            activity_log_views.create_log(request.user, "deleted organization")
        except Exception as err:
            print(str(err))

        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {}
        }, status=status.HTTP_200_OK)


