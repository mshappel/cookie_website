import logging

from django.http import HttpResponse

from accounts.models import CustomUser
from cookie_booths.models import BoothBlock
from cookie_booths.views.helpers.user_identification import get_owner_and_user_type
from cookie_booths.views.helpers.permissions import get_permission_level
from troops.models import Troop
from utils.display_message import load_error_messages

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

error_messages = load_error_messages()

ORDERING_FIELDS = ["booth_day__booth", "booth_day", "booth_block_start_time"]


def get_booth_context(request, time_threshold):
    # Get owner and user type
    owner, is_daisy_troop, is_cookie_captain = get_owner_and_user_type(request)
    if owner is None:
        return HttpResponse(error_messages["unexpected_user"], status=403)

    # Retrieve booth blocks with combined filters
    selected_booth_blocks = BoothBlock.objects.retrieve_booth_blocks(
        is_daisy_troop, is_cookie_captain, time_threshold, ORDERING_FIELDS
    )

    # Initialize booth information list
    booth_information = []

    for booth in selected_booth_blocks:
        current_booth_information = create_booth_information(booth, owner, is_cookie_captain)
        booth_information.append(current_booth_information)

    permission_level = get_permission_level(request.user, is_daisy_troop, is_cookie_captain)

    # Troop list only needed for an admin
    if permission_level == "admin":
        # Retrieve available troops
        available_troop_list = retrieve_available_troops
    else:
        available_troop_list = None

    return {
        "booth_blocks": booth_information,
        "available_troops": available_troop_list,
        "permission_level": permission_level,
    }


def is_booth_owned_by_current_user(booth: BoothBlock, owner, is_cookie_captain):
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


def get_cookie_captain_email_message(booth_block: BoothBlock):
    booth_owner: CustomUser = booth_block.booth_block_current_owner
    return (
        f"Cookie Captain: {booth_owner.first_name} {booth_owner.last_name} || "
        f"Contact: {booth_owner.email}"
    )


def create_booth_information(booth_block: BoothBlock, owner, is_cookie_captain):
    booth_owned_by_current_user = is_booth_owned_by_current_user(
        booth_block, owner, is_cookie_captain
    )
    booth_owned_by_cookie_captain = booth_block.is_owner_custom_user()
    if booth_owned_by_cookie_captain:
        cookie_cap_email_message = get_cookie_captain_email_message(booth_block)
    else:
        cookie_cap_email_message = None

    return {
        "booth_block_information": booth_block,
        "booth_owned_by_current_user": booth_owned_by_current_user,
        "booth_owned_by_cookie_captain": booth_owned_by_cookie_captain,
        "booth_block_cookie_captain_email": cookie_cap_email_message,
    }


def retrieve_available_troops():
    return Troop.objects.order_by("troop_number")
