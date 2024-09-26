from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from clinic import models as clinic_model
from clinic import serializers as clinic_serializer


class ClinicDropDownListApi(APIView):
    # Dev: Fakhrul Islam Fahad
    # Date: 21 Dec 2023
    # purpose : clinic for dropdown

    serializer_class = clinic_serializer.ClinicDropDownSerializer

    def get(self, request):
        clinic_instances = clinic_model.Clinic.objects.filter(deleted_at=None, is_active=True)
        serializer = self.serializer_class(clinic_instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
