from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.http import Http404
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from datetime import datetime
from django.utils import timezone
from user_management import serializers as user_management_serializer
from user_management import models as user_management_models
from organization import models as organization_models
from location import models as location_model
from .helper_class import *
from lib.permission import Action, PermissionManager, Module
from lib.response.type import ResponseType
from Activity_log import views as activity_log_views


class UserCreateMobileApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 21 Dec 2023
    purpose : user create from mobile
    """

    user_create_serializer = user_management_serializer.UserCreateSerializer
    user_profile_serializer = user_management_serializer.UserProfileSerializer
    user_organization_serializer = user_management_serializer.UserOrganizationSerializer
    user_location_serializer = user_management_serializer.UserLocationSerializer
    user_clinic_serializer = user_management_serializer.UserClinicSerializer
    role_serializer = user_management_serializer.UserRoleSerializer
    user_details_serializer = user_management_serializer.UserDetailsSerializer

    def post(self, request):
        try:
            data = request.data.copy()
            user_data = data['user'] if 'user' in data else None
            user_profile_data = data['profile'] if 'profile' in data else None
            location_data = data['location'] if 'location' in data else None
            clinic_data = data['clinic'] if 'clinic' in data else None

            if user_data and user_profile_data and location_data and clinic_data:
                with transaction.atomic():
                    # user section
                    if user_data["password"] != UserValidation.password_checker(user_data["password"]):
                        return Response({
                            ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                            ResponseType.MESSAGE: UserValidation.password_checker(user_data["password"]),
                            ResponseType.DATA: {}
                        }, status=status.HTTP_400_BAD_REQUEST)

                    profile_instance_for_email = user_management_model.UserModuleProfile.objects.filter(
                        email=user_profile_data['email'])
                    profile_instance_for_phone = user_management_model.UserModuleProfile.objects.filter(
                        phone=user_profile_data['phone'])

                    if len(profile_instance_for_email) or len(profile_instance_for_phone):
                        return Response({
                            ResponseType.STATUS : status.HTTP_400_BAD_REQUEST,
                            ResponseType.MESSAGE: "email/phone exist in the system",
                            ResponseType.DATA: {}
                        }, status=status.HTTP_400_BAD_REQUEST)

                    try:
                        user_data.update({
                            "username": UserValidation.generate_username(
                                location_data[0]['field_name'],
                                user_profile_data['phone']
                            )
                        })

                        user_serializer = self.user_create_serializer(data=user_data)
                        user_serializer.is_valid(raise_exception=True)
                        user_serializer.save()
                    except:
                        transaction.set_rollback(True)
                        return Response(
                            {
                                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                ResponseType.DATA: {},
                                ResponseType.MESSAGE: ""
                            }, status=status.HTTP_400_BAD_REQUEST)

                    # user profile section
                    user_profile_data.update({
                        "user": user_serializer.data['id']
                    })
                    profile_serializer = self.user_profile_serializer(data=user_profile_data)
                    if profile_serializer.is_valid(raise_exception=True):
                        profile_serializer.save()
                    else:
                        transaction.set_rollback(True)
                        Response({
                            ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                            ResponseType.DATA: {},
                            ResponseType.MESSAGE: str(profile_serializer.errors)
                        }, status=status.HTTP_400_BAD_REQUEST)

                    # location section

                    user_loc = []
                    for geodata in location_data:
                        try:
                            location_instance = location_model.GeoData.objects.get(geocode=geodata['geocode'])
                            user_location_instance = user_management_models.UserLoc.objects.filter(
                                deleted_at=None, location=location_instance.id
                            )
                            if len(user_location_instance) > 0:
                                transaction.set_rollback(True)
                                return Response({
                                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                    ResponseType.MESSAGE: "User already allocated in this location",
                                    ResponseType.DATA: {}
                                }, status=status.HTTP_400_BAD_REQUEST)
                            user_loc.append({
                                "user": user_serializer.data['id'],
                                "location": location_instance.id
                            })
                        except Exception as err:
                            transaction.set_rollback(True)
                            print("error geodata")
                            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

                    user_loc_serializer = self.user_location_serializer(data=user_loc, many=True)
                    if user_loc_serializer.is_valid(raise_exception=True):
                        user_loc_serializer.save()
                    else:
                        transaction.set_rollback(True)
                        print("error user_loc_serializer")
                        return Response({
                            ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                            ResponseType.DATA: {},
                            ResponseType.MESSAGE: str(user_loc_serializer.errors)
                        },
                                        status=status.HTTP_400_BAD_REQUEST)

                    # clinic section
                    try:
                        user_clinic = []
                        for clinic in clinic_data:
                            user_clinic.append({
                                "user": user_serializer.data['id'],
                                "clinic": clinic['clinic']
                            })

                        user_clinic_serializer = self.user_clinic_serializer(data=user_clinic, many=True)
                        if user_clinic_serializer.is_valid(raise_exception=True):
                            user_clinic_serializer.save()
                        else:
                            transaction.set_rollback(True)
                            return Response({
                                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                ResponseType.MESSAGE: str(user_clinic_serializer.errors),
                                ResponseType.DATA: {}
                            }, status=status.HTTP_400_BAD_REQUEST)

                    except Exception as err:
                        print("error user_clinic_serializer", str(err))
                        transaction.set_rollback(True)
                        return Response({
                            {
                                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                ResponseType.MESSAGE: str(err),
                                ResponseType.DATA: {}
                            }
                        }, status=status.HTTP_400_BAD_REQUEST)

                    # role section
                    try:
                        role_instance = user_management_model.Role.objects.get(role_name='Facilitator')
                        role_data = {
                            "user": user_serializer.data['id'],
                            "role": role_instance.id
                        }
                        r_serializer = self.role_serializer(data=role_data)
                        if r_serializer.is_valid(raise_exception=True):
                            try:
                                activity_log_views.create_log(request.user, "created user")
                            except Exception as err:
                                print(str(err))

                            r_serializer.save()
                        else:
                            return Response({
                                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                ResponseType.MESSAGE: str(r_serializer.errors),
                                ResponseType.DATA: {}
                            }, status=status.HTTP_400_BAD_REQUEST)

                    except Exception as err:
                        transaction.set_rollback(True)
                        print("error user_role_serializer")
                        return Response({
                                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                ResponseType.MESSAGE: str(err),
                                ResponseType.DATA: {}
                            }, status=status.HTTP_400_BAD_REQUEST)

                return Response({
                    ResponseType.STATUS: status.HTTP_201_CREATED,
                    ResponseType.MESSAGE: "success",
                    ResponseType.DATA: self.user_details_serializer(
                        user_management_model.User.objects.get(id=user_serializer.data['id']), many=False
                    ).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: "user, profile, organization, location, clinic data mandatory",
                    ResponseType.DATA: {}
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            print("error last", str(err))
            return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: str(err),
                    ResponseType.DATA: {}
                }, status=status.HTTP_400_BAD_REQUEST)


class UserCreateWebApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 21 Dec 2023
    purpose : user create from mobile
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.USER
    action = Action.ADD

    user_create_serializer = user_management_serializer.UserCreateSerializer
    user_profile_serializer = user_management_serializer.UserProfileSerializer
    user_organization_serializer = user_management_serializer.UserOrganizationSerializer
    user_location_serializer = user_management_serializer.UserLocationSerializer
    user_clinic_serializer = user_management_serializer.UserClinicSerializer
    role_serializer = user_management_serializer.UserRoleSerializer
    user_details_serializer = user_management_serializer.UserDetailsSerializer

    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data.copy()
                print(data, '==========')
                user_data = data['user'] if 'user' in data else None
                user_profile_data = data['profile'] if 'profile' in data else None
                location_data = data['location'] if 'location' in data else None
                clinic_data = data['clinic'] if 'clinic' in data else None
                organization_data = data['organization'] if 'organization' in data else None
                role_data = data['role'] if 'role' in data else None

                if user_data and user_profile_data and location_data and role_data:

                    # user section
                    if user_data["password"] != UserValidation.password_checker(user_data["password"]):
                        return Response({
                            ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                            ResponseType.MESSAGE: UserValidation.password_checker(user_data["password"]),
                            ResponseType.DATA: {}
                        }, status=status.HTTP_400_BAD_REQUEST)

                    profile_instance_for_email = user_management_model.UserModuleProfile.objects.filter(
                        email=user_profile_data['email'])
                    profile_instance_for_phone = user_management_model.UserModuleProfile.objects.filter(
                        phone=user_profile_data['phone'])

                    if len(profile_instance_for_email) or len(profile_instance_for_phone):
                        return Response({
                            ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                            ResponseType.MESSAGE: "email/phone exist in the system",
                            ResponseType.DATA: {}
                        }, status=status.HTTP_400_BAD_REQUEST)

                    try:
                        user_data.update({
                            "username": UserValidation.generate_username(
                                location_data[0]['field_name'],
                                user_profile_data['phone']
                            )
                        })

                        user_serializer = self.user_create_serializer(data=user_data)
                        user_serializer.is_valid(raise_exception=True)
                        user_serializer.save()
                    except:
                        transaction.set_rollback(True)
                        return Response(
                            {
                                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                ResponseType.DATA: {},
                                ResponseType.MESSAGE: ""
                            }, status=status.HTTP_400_BAD_REQUEST)

                    # user profile section
                    user_profile_data.update({
                        "user": user_serializer.data['id']
                    })
                    profile_serializer = self.user_profile_serializer(data=user_profile_data)
                    if profile_serializer.is_valid(raise_exception=True):
                        profile_serializer.save()
                    else:
                        Response({
                            ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                            ResponseType.DATA: {},
                            ResponseType.MESSAGE: str(profile_serializer.errors)
                        }, status=status.HTTP_400_BAD_REQUEST)

                    # location section

                    user_loc = []
                    for geodata in location_data:
                        try:
                            location_instance = location_model.GeoData.objects.get(geocode=geodata['geocode'])
                            user_location_instance = user_management_models.UserLoc.objects.filter(
                                deleted_at=None, location=location_instance.id
                            )
                            if len(user_location_instance) > 0:
                                transaction.set_rollback(True)
                                return Response({
                                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                    ResponseType.MESSAGE: "User already allocated in this location",
                                    ResponseType.DATA: {}
                                }, status=status.HTTP_400_BAD_REQUEST)
                            user_loc.append({
                                "user": user_serializer.data['id'],
                                "location": location_instance.id
                            })
                        except Exception as err:
                            transaction.set_rollback(True)
                            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

                    user_loc_serializer = self.user_location_serializer(data=user_loc, many=True)
                    if user_loc_serializer.is_valid(raise_exception=True):
                        user_loc_serializer.save()
                    else:
                        return Response({
                            ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                            ResponseType.DATA: {},
                            ResponseType.MESSAGE: str(user_loc_serializer.errors)
                        }, status=status.HTTP_400_BAD_REQUEST)

                    # clinic section
                    if clinic_data:
                        try:
                            user_clinic = []
                            for clinic in clinic_data:
                                user_clinic_instance = user_management_models.UserClinic.objects.filter(
                                    deleted_at=None, clinic_id=clinic['clinic']
                                )
                                if len(user_clinic_instance) > 0:
                                    transaction.set_rollback(True)
                                    return Response({
                                        ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                        ResponseType.MESSAGE: "User already allocated in this Clinic",
                                        ResponseType.DATA: {}
                                    }, status=status.HTTP_400_BAD_REQUEST)
                                user_clinic.append({
                                    "user": user_serializer.data['id'],
                                    "clinic": clinic['clinic']
                                })
                            user_clinic_serializer = self.user_clinic_serializer(data=user_clinic, many=True)
                            if user_clinic_serializer.is_valid(raise_exception=True):
                                user_clinic_serializer.save()
                            else:
                                return Response({
                                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                    ResponseType.MESSAGE: str(user_clinic_serializer.errors),
                                    ResponseType.DATA: {}
                                }, status=status.HTTP_400_BAD_REQUEST)

                        except Exception as err:
                            transaction.set_rollback(True)
                            return Response(
                                {
                                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                    ResponseType.MESSAGE: str(err),
                                    ResponseType.DATA: {}
                                }
                            , status=status.HTTP_400_BAD_REQUEST)

                    # role section
                    try:
                        role_instance = user_management_model.Role.objects.get(id=role_data['role'])
                        role_data = {
                            "user": user_serializer.data['id'],
                            "role": role_instance.id
                        }
                        r_serializer = self.role_serializer(data=role_data)
                        if r_serializer.is_valid(raise_exception=True):
                            r_serializer.save()
                        else:
                            return Response({
                                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                ResponseType.MESSAGE: str(r_serializer.errors),
                                ResponseType.DATA: {}
                            }, status=status.HTTP_400_BAD_REQUEST)

                    except Exception as err:
                        transaction.set_rollback(True)
                        return Response({
                                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                ResponseType.MESSAGE: str(err),
                                ResponseType.DATA: {}
                            }, status=status.HTTP_400_BAD_REQUEST)

                    # organization
                    if organization_data and organization_data['organization']:
                        try:
                            organization_instance = organization_models.Organization.objects.get(
                                id=organization_data['organization']
                            )
                            organization_data = {
                                "user": user_serializer.data['id'],
                                "organization": organization_instance.id
                            }
                            org_serializer = self.user_organization_serializer(data=organization_data)
                            if org_serializer.is_valid(raise_exception=True):
                                try:
                                    activity_log_views.create_log(request.user, "created user")
                                except Exception as err:
                                    print(str(err))
                                org_serializer.save()
                            else:
                                return Response({
                                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                    ResponseType.MESSAGE: str(org_serializer.errors),
                                    ResponseType.DATA: {}
                                }, status=status.HTTP_400_BAD_REQUEST)
                        except Exception as err:
                            transaction.set_rollback(True)
                            return Response({
                                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                                ResponseType.MESSAGE: str(err),
                                ResponseType.DATA: {}
                            }, status=status.HTTP_400_BAD_REQUEST)

                    return Response({
                        ResponseType.STATUS: status.HTTP_201_CREATED,
                        ResponseType.MESSAGE: "success",
                        ResponseType.DATA: self.user_details_serializer(
                            user_management_model.User.objects.get(id=user_serializer.data['id']), many=False
                        ).data
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                        ResponseType.MESSAGE: "user, profile, organization, location, clinic data mandatory",
                        ResponseType.DATA: {}
                    }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: str(err),
                    ResponseType.DATA: {}
                }, status=status.HTTP_400_BAD_REQUEST)


class UserDetailsApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 11 Mar 2023
    purpose : user delete
    url : /api/user-management/details
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.USER
    action = Action.READ

    serializer_class = user_management_serializer.UserDetailsSerializer

    def post(self, request):
        data = request.data.copy()
        try:
            user_instance = user_management_models.User.objects.get(
                deleted_at=None, id=data['id']
            )
            serializer = self.serializer_class(user_instance, many=False)

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


class UserShortDetailsApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 27 Dec 2023
    purpose : get email and phone number for user
    """
    def post(self, request):
        data = request.data.copy()
        try:
            user_instance = user_management_model.User.objects.get(**data)
            return Response({
                "email": user_instance.userprofile.email,
                "phone": user_instance.userprofile.phone
            }, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_200_OK)


class UserProfilePictureUpdateApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 21 Dec 2023
    purpose : user profile picture update
    url : /api/user-management/profile-picture-update
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.USER
    action = Action.EDIT

    serializer_class = user_management_serializer.UserProfileSerializer

    def get_object(self, id):
        try:
            return user_management_model.UserModuleProfile.objects.get(user_id=id)
        except user_management_model.UserModuleProfile.DoesNotExist:
            return Http404

    def post(self, request):
        data = request.data.copy()
        user_profile_instance = self.get_object(data['id'])
        serializer = self.serializer_class(user_profile_instance, data={"picture": request.FILES['picture']},
                                           partial=True)
        if serializer.is_valid(raise_exception=True):
            try:
                activity_log_views.create_log(request.user, "updated user")
            except Exception as err:
                print(str(err))
            serializer.save()
            return Response({
                ResponseType.STATUS: status.HTTP_200_OK,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA: serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
            ResponseType.MESSAGE: str(serializer.errors),
            ResponseType.DATA: {}
        }, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordResetApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 31 Dec 2023
    purpose : user password reset
    url : /api/user-management/password-reset
    """

    serializer_class = user_management_serializer.UserCreateSerializer

    def get_object(self, username):
        try:
            return user_management_model.User.objects.get(username=username)
        except:
            return Http404

    def post(self, request):
        data = request.data.copy()
        if data['password'] != UserValidation.password_checker(data["password"]):
            return Response({"error": UserValidation.password_checker(data["password"])},
                            status=status.HTTP_400_BAD_REQUEST)
        user_instance = self.get_object(data['username'])
        serializer = self.serializer_class(user_instance, data={"password": make_password(data['password'])},
                                           partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response({"error": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)


class PendingUserListApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 7 Mar 2024
    purpose : show pending user
    url : /api/user-management/pending-user/list
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.PENDING_USER
    action = Action.READ

    pagination_class = PageNumberPagination
    serializer_class = user_management_serializer.UserDetailsSerializer

    def get(self, request):
        search = request.GET.get('search')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        rejected_user_instance = user_management_model.UserReject.objects.filter(deleted_at=None).values_list('user')
        user_instances = user_management_model.User.objects.filter(
            deleted_at=None, is_active=False, is_superuser=False
        ).exclude(id__in=rejected_user_instance)

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['created_at__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['created_at__date__lte'] = to_date
        if search:
            user_instances = user_instances.filter(
                Q(username__icontains=search) | Q(userprofile__first_name__icontains=search)
            )
        user_instances = user_instances.filter(**filter_object)

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(user_instances, request)
        serializer = self.serializer_class(paginated_queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)

        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": paginated_data.data["count"],
                "results": paginated_data.data["results"]
            }
        }, status=status.HTTP_200_OK)


class UserActiveApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 7 Mar 2024
    purpose : show pending user
    url : /api/user-management/pending-user/update
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.PENDING_USER
    action = Action.EDIT

    def post(self, request):
        data = request.data.copy()
        try:
            user_instance = user_management_model.User.objects.get(
                deleted_at=None, id=data['id']
            )
            user_instance.is_active = True
            user_instance.updated_at = datetime.now()
            user_instance.updated_by = request.user
            user_instance.save()

            try:
                activity_log_views.create_log(request.user, "activated user")
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


class UserRejectApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 7 Mar 2024
    purpose : show pending user
    url :  /api/user-management/pending-user/reject
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.PENDING_USER
    action = Action.EDIT

    def post(self, request):
        try:
            data = request.data.copy()
            user_instance = user_management_model.User.objects.get(
                deleted_at=None, id=data['id']
            )
            user_management_model.UserReject.objects.create(user=user_instance)

            try:
                activity_log_views.create_log(request.user, "rejected user")
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


class UserListApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 10 Mar 2023
    purpose : user profile picture update
    url : /api/user-management/list
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.USER
    action = Action.READ

    serializer_class = user_management_serializer.UserDetailsSerializer
    pagination_class = PageNumberPagination

    def get(self, request):
        search = request.GET.get('search')
        from_value = request.GET.get('from')
        to_value = request.GET.get('to')

        user_instances = user_management_models.User.objects.filter(deleted_at=None, is_superuser=False)

        filter_object = {}
        if from_value:
            from_date = timezone.make_aware(datetime.strptime(from_value, "%Y-%m-%d"))
            filter_object['created_at__date__gte'] = from_date
        if to_value:
            to_date = timezone.make_aware(datetime.strptime(to_value, "%Y-%m-%d"))
            filter_object['created_at__date__lte'] = to_date
        if search:
            user_instances = user_instances.filter(
                Q(userprofile__first_name__icontains=search) |
                Q(userprofile__phone__icontains=search)
            )
        user_instances = user_instances.filter(**filter_object).order_by("-id")
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(user_instances, request)
        serializer = self.serializer_class(paginated_queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)

        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {
                "count": paginated_data.data["count"],
                "results": paginated_data.data["results"]
            }
        }, status=status.HTTP_200_OK)


class UserDeleteApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 11 Mar 2023
    purpose : user delete
    url : /api/user-management/delete
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.USER
    action = Action.DELETE

    def post(self, request):
        data = request.data.copy()
        try:
            user_instance = user_management_models.User.objects.get(
                deleted_at=None, id=data['id']
            )
            user_instance.deleted_at = datetime.now()
            user_instance.deleted_by = request.user
            user_instance.save()

            try:
                activity_log_views.create_log(request.user, "deleted user")
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
                ResponseType.MESSAGE: str(err)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserEditApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 21 Dec 2023
    purpose : user create edit
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [PermissionManager]
    module = Module.USER
    action = Action.EDIT

    user_profile_serializer = user_management_serializer.UserProfileSerializer
    user_organization_serializer = user_management_serializer.UserOrganizationSerializer
    role_serializer = user_management_serializer.UserRoleSerializer
    user_clinic_serializer = user_management_serializer.UserClinicSerializer
    user_location_serializer = user_management_serializer.UserLocationSerializer

    def post(self, request):
        data = request.data.copy()
        print(data, '=============')
        user_profile_data = data['profile'] if 'profile' in data else None
        organization_data = data['organization'] if 'organization' in data else None
        role_data = data['role'] if 'role' in data else None
        clinic_data = data['clinic'] if 'clinic' in data else None
        location_data = data['location'] if 'location' in data else None

        try:
            user_instance = user_management_models.User.objects.get(id=data["id"])
        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(err),
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)

        if user_profile_data:
            if 'email' in user_profile_data:
                profile_instance_for_email = user_management_model.UserModuleProfile.objects.filter(
                    email=user_profile_data['email'])
                if len(profile_instance_for_email):
                    return Response({
                        ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                        ResponseType.MESSAGE: "Email exists in the system",
                        ResponseType.DATA: {}
                    }, status=status.HTTP_400_BAD_REQUEST)
            if 'phone' in user_profile_data:
                profile_instance_for_phone = user_management_model.UserModuleProfile.objects.filter(
                    phone=user_profile_data['phone'])
                if len(profile_instance_for_phone):
                    return Response({
                        ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                        ResponseType.MESSAGE: "Phone number exist in the system",
                        ResponseType.DATA: {}
                    }, status=status.HTTP_400_BAD_REQUEST)

            try:
                user_profile_instance = user_management_models.UserModuleProfile.objects.get(user_id=user_instance.id)
                profile_serializer = self.user_profile_serializer(
                    user_profile_instance, data=user_profile_data, partial=True
                )
                if profile_serializer.is_valid():
                    profile_serializer.save(updated_at=datetime.now(), updated_by=request.user)
                else:
                    return Response({
                        ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                        ResponseType.MESSAGE: str(profile_serializer.errors),
                        ResponseType.DATA: {}
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as err:
                return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: str(err),
                    ResponseType.DATA: {}
                }, status=status.HTTP_400_BAD_REQUEST)

        if organization_data:
            if len(user_management_models.UserOrganization.objects.filter(user_id=user_instance.id)):
                try:
                    user_organization_instance = user_management_models.UserOrganization.objects.get(
                        user_id=user_instance.id
                    )
                    user_org_serializer = self.user_organization_serializer(
                        user_organization_instance, data={
                            "user": user_instance.id,
                            "organization": organization_data["organization"]
                        },
                        partial=True
                    )
                    if user_org_serializer.is_valid():
                        user_org_serializer.save(updated_at=datetime.now(), updated_by=request.user)
                    else:
                        return Response({
                            ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                            ResponseType.MESSAGE: str(user_org_serializer.errors),
                            ResponseType.DATA: {}
                        }, status=status.HTTP_400_BAD_REQUEST)
                except Exception as err:
                    return Response({
                        ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                        ResponseType.MESSAGE: str(err),
                        ResponseType.DATA: {}
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    organization_instance = organization_models.Organization.objects.get(
                        id=organization_data['organization']
                    )
                    organization_data = {
                        "user": user_instance.id,
                        "organization": organization_instance.id
                    }
                    org_serializer = self.user_organization_serializer(data=organization_data)
                    if org_serializer.is_valid():
                        org_serializer.save()
                    else:
                        return Response({
                            ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                            ResponseType.MESSAGE: str(org_serializer.errors),
                            ResponseType.DATA: {}
                        }, status=status.HTTP_400_BAD_REQUEST)
                except Exception as err:
                    transaction.set_rollback(True)
                    return Response({
                        ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                        ResponseType.MESSAGE: str(err),
                        ResponseType.DATA: {}
                    }, status=status.HTTP_400_BAD_REQUEST)

        if role_data:
            try:
                user_role_instance = user_management_models.UserRole.objects.get(
                    user_id=user_instance.id
                )
                r_serializer = self.role_serializer(user_role_instance, data={
                    "user": user_instance.id,
                    "role": role_data["role"]
                })
                if r_serializer.is_valid():
                    r_serializer.save(updated_at=datetime.now(), updated_by=request.user)
                else:
                    return Response({
                        ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                        ResponseType.MESSAGE: str(r_serializer.errors),
                        ResponseType.DATA: {}
                    }, status=status.HTTP_400_BAD_REQUEST)

            except Exception as err:
                return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.MESSAGE: str(err),
                    ResponseType.DATA: {}
                }, status=status.HTTP_400_BAD_REQUEST)

        if clinic_data:
            user_management_models.UserClinic.objects.filter(user_id=user_instance.id).delete()
            try:
                user_clinic = []
                for clinic in clinic_data:
                    user_clinic.append({
                        "user": user_instance.id,
                        "clinic": clinic['clinic']
                    })
                user_clinic_serializer = self.user_clinic_serializer(data=user_clinic, many=True)
                if user_clinic_serializer.is_valid(raise_exception=True):
                    user_clinic_serializer.save()
                else:
                    return Response({
                        ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                        ResponseType.MESSAGE: str(user_clinic_serializer.errors),
                        ResponseType.DATA: {}
                    }, status=status.HTTP_400_BAD_REQUEST)

            except Exception as err:
                transaction.set_rollback(True)
                return Response(
                    {
                        ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                        ResponseType.MESSAGE: str(err),
                        ResponseType.DATA: {}
                    }
                    , status=status.HTTP_400_BAD_REQUEST)

        if location_data:
            user_management_models.UserLoc.objects.filter(
                user_id=user_instance.id
            ).delete()

            user_loc = []
            for geodata in location_data:
                try:
                    location_instance = location_model.GeoData.objects.get(geocode=geodata['geocode'])
                    user_loc.append({
                        "user": user_instance.id,
                        "location": location_instance.id
                    })
                except Exception as err:
                    transaction.set_rollback(True)
                    return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

            user_loc_serializer = self.user_location_serializer(data=user_loc, many=True)
            if user_loc_serializer.is_valid(raise_exception=True):
                user_loc_serializer.save()
            else:
                return Response({
                    ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                    ResponseType.DATA: {},
                    ResponseType.MESSAGE: str(user_loc_serializer.errors)
                }, status=status.HTTP_400_BAD_REQUEST)
        try:
            activity_log_views.create_log(request.user, "updated user")
        except Exception as err:
            print(str(err))
        return Response({
            ResponseType.STATUS: status.HTTP_200_OK,
            ResponseType.MESSAGE: "success",
            ResponseType.DATA: {}
        }, status=status.HTTP_200_OK)


class UserEmailValidation(APIView):
    def post(self, request):
        data = request.data.copy()
        try:
            user_instance = user_management_models.UserModuleProfile.objects.get(
                deleted_at=None, email=data['email']
            )
            return Response({
                ResponseType.STATUS:status.HTTP_200_OK,
                ResponseType.MESSAGE: "success",
                ResponseType.DATA:{}
            }, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({
                ResponseType.STATUS:status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: "This email is not found in this system",
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordUpdateByEmail(APIView):
    serializer_class = user_management_serializer.UserCreateSerializer

    def get_object(self, email):
        try:

            return
        except:
            return Http404

    def post(self, request):
        data = request.data.copy()
        print(data, "=======")
        if data['password'] != UserValidation.password_checker(data["password"]):
            return Response({"error": UserValidation.password_checker(data["password"])},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            user_profile_instance = user_management_model.UserModuleProfile.objects.get(email=data['email'],
                                                                                        deleted_at=None)
            print(user_profile_instance, "=============")
            user_instance = user_management_models.User.objects.get(id=user_profile_instance.user.id)
            serializer = self.serializer_class(user_instance, data={"password": make_password(data['password'])},
                                               partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK)
            return Response({"error": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({
                ResponseType.STATUS: status.HTTP_400_BAD_REQUEST,
                ResponseType.MESSAGE: str(err),
                ResponseType.DATA: {}
            }, status=status.HTTP_400_BAD_REQUEST)


