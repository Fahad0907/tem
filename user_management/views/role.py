from rest_framework.views import APIView
from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response
from user_management import models as user_management_models
from user_management import serializers as user_management_serializers
from lib.response.type import ResponseType


class RoleListDropDown(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 2 jan 2024
    purpose : meeting create
    url : api/user-management/role/list/drop-down
    """

    serializer_class = user_management_serializers.RoleDropDownSerializer

    def get(self, request):
        role_instances = user_management_models.Role.objects.filter(
            deleted_at=None, is_active=True
        )
        serializer = self.serializer_class(role_instances, many=True)
        return Response(serializer.data)


class RoleList(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 2 jan 2024
    purpose : meeting create
    url : api/user-management/role/list
    """

    serializer_class = user_management_serializers.RoleSerializer

    def get(self, request):
        search = request.GET.get('search')
        role_instances = user_management_models.Role.objects.filter(deleted_at=None, is_active=True)
        if search:
            role_instances = role_instances.filter(role_name__icontains=search)

        serializer = self.serializer_class(role_instances, many=True)
        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: serializer.data
        })
