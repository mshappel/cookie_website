import logging

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
    booth_information = _create_booth_information_list(
        selected_booth_blocks=selected_booth_blocks,
        owner=owner,
        is_cookie_captain=is_cookie_captain,
    )
    permission_level = permissions.get_permission_level(
        user=request.user,
        is_daisy_troop=is_daisy_troop,
        is_cookie_captain=is_cookie_captain,
    )
    available_troop_list = _get_available_troop_list(permission_level)

    return {
        "booth_blocks": booth_information,
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
    if permission_level == "admin":
        return retrieve_available_troops()
    return None


def _create_booth_information_list(selected_booth_blocks, owner, is_cookie_captain):
    """
    Create a list of booth information from the selected booth blocks.

    Args:
        selected_booth_blocks (QuerySet): The selected booth blocks.
        owner (User): The owner of the booth blocks.
        is_cookie_captain (bool): Whether the user is a cookie captain.

    Returns:
        list: A list of booth information dictionaries.
    """
    booth_information = []
    for booth in selected_booth_blocks:
        current_booth_information = _create_booth_information(
            booth_block=booth,
            owner=owner,
            is_cookie_captain=is_cookie_captain,
        )
        booth_information.append(current_booth_information)
    return booth_information


def _is_booth_owned_by_current_user(booth: BoothBlock, owner, is_cookie_captain):
    booth_owner = booth.booth_block_current_owner
    daisy_booth_owner = booth.booth_block_daisy_troop_owner
    is_owned_by_booth_owner = booth_owner == owner
    is_owned_by_daisy_troop_owner = daisy_booth_owner == owner

    if owner is None:
        return False
    elif is_cookie_captain:
        return is_owned_by_booth_owner
    else:
        return is_owned_by_booth_owner or is_owned_by_daisy_troop_owner


def _get_cookie_captain_email_message(booth_block: BoothBlock):
    booth_owner: CustomUser = booth_block.booth_block_current_owner
    return (
        f"Cookie Captain: {booth_owner.first_name} {booth_owner.last_name} || "
        f"Contact: {booth_owner.email}"
    )


def _create_booth_information(booth_block: BoothBlock, owner, is_cookie_captain):
    booth_owned_by_current_user = _is_booth_owned_by_current_user(
        booth_block, owner, is_cookie_captain
    )
    booth_owned_by_cookie_captain = booth_block.is_owner_custom_user()
    if booth_owned_by_cookie_captain:
        cookie_cap_email_message = _get_cookie_captain_email_message(booth_block)
    else:
        cookie_cap_email_message = None

    return {
        "booth_block_information": booth_block,
        "booth_owned_by_current_user": booth_owned_by_current_user,
        "booth_owned_by_cookie_captain": booth_owned_by_cookie_captain,
        "booth_block_cookie_captain_email": cookie_cap_email_message,
    }


# TODO: MOVE THIS TO A MANAGER
def retrieve_available_troops():
    return Troop.objects.order_by("troop_number")
