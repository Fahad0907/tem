from rest_framework.views import APIView
from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import datetime
from user_management import models as user_management_models
from user_management import serializers as user_management_serializers
from lib.permission import Action, PermissionManager, Module
from lib.response.type import ResponseType
from Activity_log import views as activity_log_views


class PermissionList(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 4 March 2024
    purpose : meeting create
    url : /api/user-management/permission/list/1
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.PERMISSION_CONTROL
    action = Action.READ
    serializer_class = user_management_serializers.PermissionSerializer

    def get(self, request, id):
        role_instances = user_management_models.Role.objects.get(
            deleted_at=None, id=id
        )
        serializer = self.serializer_class(role_instances, many=False)
        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: serializer.data
        }, status=status.HTTP_200_OK)


class PermissionUpdate(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 4 march 2024
    purpose : meeting create
    url : /api/user-management/permission/update
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.PERMISSION_CONTROL
    action = Action.EDIT

    def post(self, request):
        try:
            data = request.data.copy()
            module_role_action_instance = user_management_models.RoleWithModuleActionMap.objects.get(
               id=data['id'], deleted_at=None
            )
            module_role_action_instance.permission = data['permission']
            module_role_action_instance.updated_at = datetime.now()
            module_role_action_instance.updated_by = request.user
            module_role_action_instance.save()
            try:
                activity_log_views.create_log(request.user, "updated permission")
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
