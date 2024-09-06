import logging
from datetime import datetime

from django.http import HttpRequest, HttpResponse

from accounts.models import CustomUser as User
from cookie_booths.models import BoothBlock
from cookie_booths.views.helpers import permissions
from troops.models import Troop
from utils.display_message import MessageLoader

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

message_loader = MessageLoader()
error_messages = message_loader.load_error_messages()
success_messages = message_loader.load_success_messages()
warning_messages = message_loader.load_warning_messages()


def get_booth_context(request: HttpRequest, time_threshold: datetime) -> dict:
    """
    Get the context for booth blocks based on the request and time threshold.

    Args:
        request (HttpRequest): The HTTP request object.
        time_threshold (datetime): The time threshold for filtering booth blocks.

    Returns:
        dict: The context dictionary containing booth blocks, available troops, and permission level.
    """
    _logger.info("Getting booth context.")
    requestor: User = request.user
    requestor_email = requestor.email

    if requestor_email is None:
        return HttpResponse(error_messages["unexpected_user"], status=403)

    is_daisy_troop: bool = Troop.objects.is_daisy_troop_by_email(requestor_email)

    # Process each booth block to determine its state and permissions
    processed_booth_information = BoothBlock.objects.retrieve_and_process_booth_information(
        time_threshold=time_threshold, request_user=requestor
    )
    _logger.debug("Processed booth information: %s", processed_booth_information)

    # Get permission level
    permission_level = permissions.get_permission_level(
        requestor=requestor,
        is_daisy_troop=is_daisy_troop,
    )
    _logger.debug("Permission level: %s", permission_level)

    # Get available troop list
    available_troop_list = _get_available_troop_list(permission_level)
    _logger.debug("Available troop list: %s", available_troop_list)
    _logger.info("Booth context retrieved successfully.")

    return {
        "booth_blocks": processed_booth_information,
        "available_troops": available_troop_list,
        "permission_level": permission_level,
    }


def _get_available_troop_list(permission_level):
    """
    Get the available troop list based on the permission level.

    Args:
        permission_level (str): The permission level of the user.

    Returns:
        list or None: The available troop list if the user is an admin, otherwise None.
    """
    if permission_level == permissions.PermissionLevel.ADMIN:
        return Troop.objects.troops_ordered_by_troop_number()
    return None
