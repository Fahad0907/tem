from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Check if it's a 401 or 403 error
        if response.status_code == status.HTTP_401_UNAUTHORIZED or response.status_code == status.HTTP_403_FORBIDDEN:
            custom_data = {
                'status': response.status_code,
                'message': 'Unauthorized' if response.status_code == status.HTTP_401_UNAUTHORIZED else 'You do not have permission to perform the desired task',
                'data': {}
            }
            response.data = custom_data

    return response
