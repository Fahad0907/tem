from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from user_management import models as user_management_model
from user_management import serializers as user_management_serializer
from lib.response.type import ResponseType


class SignInApi(APIView):
    def post(self, request):
        data = request.data.copy()
        username = data['username']
        password = data['password']

        if username is None or password is None:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "please provide username and password",
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = user_management_model.User.objects.get(username=username, deleted_at=None)
            if not user.is_active:
                return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: "User inactive",
                    ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "Credential not correct",
                ResponseType.DATA:{}
            }, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "Credential not correct",
                ResponseType.DATA:{}
            }, status=status.HTTP_400_BAD_REQUEST)

        if data['type'] == 'mobile':
            try:
                user_role_instance = user_management_model.UserRole.objects.get(deleted_at=None,
                                                                                user=user,
                                                                                role__role_name='Facilitator')
                refresh = RefreshToken.for_user(user)
                tokens = {
                    'user_details': user_management_serializer.UserDetailsSerializer(user, many=False).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
                return Response({
                    ResponseType.STATUS: status.HTTP_200_OK,
                    ResponseType.MESSAGE: "success",
                    ResponseType.DATA: tokens
                }, status=status.HTTP_200_OK)

            except Exception as err:
                return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: "Only Facilitator can sign in from mobile.",
                    ResponseType.DATA: {}
                }, status=status.HTTP_400_BAD_REQUEST)

        elif data['type'] == 'web':
            try:
                user_role_instance = user_management_model.UserRole.objects.get(deleted_at=None,
                                                                                user=user,
                                                                                role__role_name='Facilitator')
                return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: "Facilitator role does not have permission to log in to the web.",
                    ResponseType.DATA: {}
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as err:
                refresh = RefreshToken.for_user(user)
                tokens = {
                    'user_details': user_management_serializer.UserDetailsSerializer(user, many=False).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
                return Response({
                    ResponseType.STATUS: status.HTTP_200_OK,
                    ResponseType.MESSAGE: "success",
                    ResponseType.DATA: tokens
                }, status=status.HTTP_200_OK)




