import logging
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status

logger = logging.getLogger("fixnet.exceptions")


class BusinessRuleViolation(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "A business rule violation occurred."
    default_code = "BUSINESS_RULE_VIOLATION"

    def __init__(self, detail=None, code=None):
        if code:
            self.default_code = code
        super().__init__(detail)


def custom_exception_handler(exc, context):
    """
    Standardized exception handler adhering to FixNet Error Handling Strategy.
    Output shape:
    {
        "error_code": "...",
        "message": "...",
        "request_id": "...",
        "details": {}
    }
    """
    response = exception_handler(exc, context)
    request = context.get("request")
    request_id = getattr(request, "request_id", "unknown_request_id") if request else "unknown_request_id"

    if response is not None:
        error_code = getattr(exc, "default_code", "API_ERROR")
        if response.status_code == 400:
            error_code = "VALIDATION_ERROR"
        elif response.status_code == 401:
            error_code = "AUTHENTICATION_FAILED"
        elif response.status_code == 403:
            error_code = "PERMISSION_DENIED"
        elif response.status_code == 404:
            error_code = "RESOURCE_NOT_FOUND"
        elif response.status_code == 429:
            error_code = "RATE_LIMIT_EXCEEDED"

        raw_data = response.data
        message = "An error occurred."
        details = {}

        if isinstance(raw_data, dict):
            if "detail" in raw_data:
                message = str(raw_data["detail"])
            else:
                details = raw_data
                message = "Validation failed for one or more fields."
        elif isinstance(raw_data, list):
            message = "; ".join([str(item) for item in raw_data])

        response.data = {
            "error_code": str(error_code).upper(),
            "message": message,
            "request_id": request_id,
            "details": details,
        }
    else:
        logger.exception("Unhandled server exception: %s (request_id=%s)", str(exc), request_id)

    return response
