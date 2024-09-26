from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from organization import models as organization_model
from organization import serializers as organization_serializer


class OrganizationListApiForDropDown(APIView):
    # Dev: Fakhrul Islam Fahad
    # Date: 21 Dec 2023
    # purpose : showing organization list in drop down

    serializer_class = organization_serializer.OrganizationDropDownSerializer

    def get(self, request):
        organization_instances = organization_model.Organization.objects.filter(deleted_at=None)
        serializer = self.serializer_class(organization_instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
