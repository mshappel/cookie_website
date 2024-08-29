import logging
from typing import List

from django.http import HttpResponse

from accounts.models import CustomUser
from cookie_booths.models import BoothBlock
from cookie_booths.views.helpers import permissions, user_identification
from troops.models import Troop
from utils.display_message import MessageLoader

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

message_loader = MessageLoader()
error_messages = message_loader.load_error_messages()
success_messages = message_loader.load_success_messages()
warning_messages = message_loader.load_warning_messages()


def get_booth_context(request, time_threshold):
    """
    Get the context for booth blocks based on the request and time threshold.

    Args:
        request (HttpRequest): The HTTP request object.
        time_threshold (datetime): The time threshold for filtering booth blocks.

    Returns:
        dict: The context dictionary containing booth blocks, available troops, and permission level.
    """
    # Get owner and user type
    owner, is_daisy_troop, is_cookie_captain = user_identification.get_owner_and_user_type(request)
    if owner is None:
        return HttpResponse(error_messages["unexpected_user"], status=403)

    # Retrieve booth blocks with combined filters
    selected_booth_blocks = BoothBlock.objects.retrieve_booth_blocks(
        is_daisy_troop=is_daisy_troop,
        is_cookie_captain=is_cookie_captain,
        time_threshold=time_threshold,
    )

    # Initialize booth information list
    booth_information = BoothBlock.objects.create_booth_information_list(
        selected_booth_blocks=selected_booth_blocks,
        owner=owner,
        is_cookie_captain=is_cookie_captain,
    )

    # Process each booth block to determine its state and permissions
    processed_booth_information = []
    for block in booth_information:
        block_info = {
            "booth_block_information": block,
            "booth_block_reserved": block.booth_block_reserved,
            "booth_block_held_for_cookie_captains": block.booth_block_held_for_cookie_captains,
            "booth_owned_by_cookie_captain": block.booth_block_current_troop_owner == owner,
            "booth_block_daisy_reserved": block.booth_block_daisy_reserved,
            "booth_block_daisy_troop_owner": block.booth_block_daisy_troop_owner,
            "booth_block_cookie_captain_email": block.booth_block_cookie_captain_email,
            "booth_owned_by_current_user": block.booth_block_current_troop_owner == request.user,
        }
        processed_booth_information.append(block_info)

    # Get permission level
    permission_level = permissions.get_permission_level(
        user=request.user,
        is_daisy_troop=is_daisy_troop,
        is_cookie_captain=is_cookie_captain,
    )

    # Get available troop list
    available_troop_list = _get_available_troop_list(permission_level)

    return {
        "booth_blocks": booth_information,
        "available_troops": available_troop_list,
        "permission_level": permission_level,
    }


def process_booth_information(booth_information: List[BoothBlock], owner, request) -> List[dict]:
    processed_booth_information = []
    for block in booth_information:
        block_info = {
            "booth_block_information": block,
            "booth_block_reserved": block.booth_block_reserved,
            "booth_block_held_for_cookie_captains": block.booth_block_held_for_cookie_captains,
            "booth_owned_by_cookie_captain": block.is_owner_custom_user(),
            "booth_block_daisy_reserved": block.booth_block_daisy_reserved,
            "booth_block_daisy_troop_owner": block.booth_block_daisy_troop_owner,
            "booth_block_cookie_captain_email": block.booth_block_current_owner.email,
            "booth_owned_by_current_user": block.booth_block_current_troop_owner == request.user,
        }
        processed_booth_information.append(block_info)
    return processed_booth_information


def _get_available_troop_list(permission_level):
    """
    Get the available troop list based on the permission level.

    Args:
        permission_level (str): The permission level of the user.

    Returns:
        list or None: The available troop list if the user is an admin, otherwise None.
    """
    if permission_level == "admin":
        return retrieve_available_troops()
    return None

# TODO: MOVE THIS TO A MANAGER
def retrieve_available_troops():
    return Troop.objects.order_by("troop_number")
