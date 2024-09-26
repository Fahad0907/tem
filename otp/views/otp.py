from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.utils import timezone
from datetime import datetime
import random
from datetime import timedelta
from otp import models as otp_model


class OtpCreateApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 27 Dec 2023
    purpose : generate otp
    url : /api/otp/create
    """
    def post(self, request):
        try:
            data = request.data.copy()
            opt_instance = otp_model.Otp.objects.filter(**data['medium'], deleted_at=None, is_checked=False)
            otp_code = random.randint(1000, 9999)
            if len(opt_instance):
                opt_instance.update(deleted_at=datetime.now(), is_checked=True)
            otp_model.Otp.objects.create(**data['medium'], type=data['type'], code=otp_code)
            if 'email' in data['medium']:
                subject = 'Otp'
                message = str(otp_code)
                from_email = 'moodlempower@gmail.com'
                recipient_list = [data['medium']['email']]
                send_mail(subject, message, from_email, recipient_list)
            return Response(status=status.HTTP_201_CREATED)
        except Exception as err:
            print("otp error==============", str(err))
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class OtpValidationApi(APIView):
    """
    Dev: Fakhrul Islam Fahad
    Date: 27 Dec 2023
    purpose : generate otp
    url /api/otp/validate
    """

    def post(self, request):
        data = request.data.copy()
        try:
            data = request.data.copy()
            opt_instance = otp_model.Otp.objects.get(**data['medium'],
                                                     code=data['code'],
                                                     type=data['type'],
                                                     deleted_at=None,
                                                     is_checked=False)
            current_time = timezone.now()
            otp_time = opt_instance.time
            time_difference = current_time - otp_time
            if time_difference > timedelta(seconds=300):
                return Response({"error": "time expired"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                opt_instance.deleted_at = datetime.now()
                opt_instance.is_checked = True
                opt_instance.save()
                return Response(status=status.HTTP_200_OK)
        except Exception as err:
            print(str(err), 'err')
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)
