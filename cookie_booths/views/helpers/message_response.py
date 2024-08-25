import logging

from django.http import JsonResponse

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


def create_message_response(message=None, is_success=False):
    message_response = {
        "message": message,
        "is_success": is_success,
    }
    _logger.debug("Message response created: %s", message_response["message"])
    _logger.debug("Is success: %s", message_response["is_success"])
    return JsonResponse(message_response)
