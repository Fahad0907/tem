from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from location import models as location_model
from location import serializers as location_serializers
import pandas as pd
import io


class LocationListApi(APIView):
    # Dev: Fakhrul Islam Fahad
    # Date: 21 Dec 2023
    # purpose : showing location
    serializer_class = location_serializers.LocationSerializer

    def get(self, request):
        geo_code = request.GET.get('geocode', None)
        if geo_code:
            try:
                location_instances = location_model.GeoData.objects.filter(
                    field_parent_id=location_model.GeoData.objects.get(geocode=geo_code, deleted_at=None).id,
                    deleted_at=None
                )
                serializer = self.serializer_class(location_instances, many=True)
                return Response(serializer.data, status.HTTP_200_OK)
            except Exception as err:
                return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        location_instances = location_model.GeoData.objects.filter(field_type_id=1, deleted_at=None)
        serializer = self.serializer_class(location_instances, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class LocationUploadApi(APIView):
    def post(self, request):
        if 'file' not in request.FILES:
            return Response("No file part in the request", status=status.HTTP_400_BAD_REQUEST)

        excel_file = request.FILES['file']
        if not excel_file.name.endswith('.xlsx'):
            return Response("Only Excel files are allowed", status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(io.BytesIO(excel_file.read()))
            for index, row in df.iterrows():
                try:
                    division = location_model.GeoData.objects.get(field_name=row["division_name"],
                                                                  geocode=row["division_code"],
                                                                  field_type_id=1)
                except:
                    division = location_model.GeoData.objects.create(field_name=row["division_name"],
                                                                     geocode=row["division_code"],
                                                                     field_type_id=1
                                                                     )
                try:
                    district = location_model.GeoData.objects.get(
                        field_name=row["district_name"],
                        geocode=row["district_code"],
                        field_type_id=2
                    )
                except:
                    district = location_model.GeoData.objects.create(
                        field_name=row["district_name"],
                        geocode=row["district_code"],
                        field_type_id=2,
                        field_parent_id=division.id
                    )
                try:
                    upazila = location_model.GeoData.objects.get(
                        field_name=row["upazila_name"],
                        geocode=row["upazila_code"],
                        field_type_id=3,
                    )
                except:
                    upazila = location_model.GeoData.objects.create(
                        field_name=row["upazila_name"],
                        geocode=row["upazila_code"],
                        field_type_id=3,
                        field_parent_id=district.id
                    )
                try:
                    union = location_model.GeoData.objects.get(
                        field_name=row["union_name"],
                        geocode=row["union_code"],
                        field_type_id=4,
                    )
                except:
                    union = location_model.GeoData.objects.create(
                        field_name=row["union_name"],
                        geocode=row["union_code"],
                        field_type_id=4,
                        field_parent_id=upazila.id
                    )
                    print(union, "========")
            return Response("File content printed successfully", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(f"Error occurred while reading the file: {str(e)}",
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClusterListApi(APIView):
    serializer_class = location_serializers.ClusterSerializer

    def get(self, request):
        cluster_instance = location_model.Cluster.objects.filter(deleted_at=None)
        serializer = self.serializer_class(cluster_instance, many=True)
        return Response({
            "message": "success",
            "status": status.HTTP_200_OK,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class DivisionBaseOnCluster(APIView):
    def post(self, request):
        data = request.data.copy()
        try:
            geo_data_instance = location_model.GeoData.objects.get(
                id=data['id']
            )
            return Response({
                "message": "success",
                "status": status.HTTP_200_OK,
                "data": {
                    "value": geo_data_instance.geocode,
                    "label": geo_data_instance.field_name
                }
            }, status=status.HTTP_200_OK)
        except Exception as err:
            Response({
                "message": str(err),
                "status": status.HTTP_400_BAD_REQUEST,
                "data": {
                    "value": geo_data_instance.geocode,
                    "label": geo_data_instance.field_name
                }
            }, status=status.HTTP_400_BAD_REQUEST)
