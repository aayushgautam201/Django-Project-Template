from rest_framework.response import Response
from rest_framework import status as http_status


def api_response(
    success=True,
    message="Request successful.",
    data=None,
    errors=None,
    status_code=http_status.HTTP_200_OK
):
    """
    Generic response formatter for Django REST Framework.
    """

    response_body = {
        "success": success,
        "message": message,
    }

    if data is not None:
        response_body["data"] = data

    if errors is not None:
        response_body["errors"] = errors

    return Response(response_body, status=status_code)
