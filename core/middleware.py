import uuid
import logging

logger = logging.getLogger("fixnet.requests")


class RequestIDMiddleware:
    """
    Ensures every incoming HTTP request carries a unique X-Request-ID
    for end-to-end tracing and correlation across logs and Celery tasks.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4()}"
        request.request_id = request_id

        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        return response
