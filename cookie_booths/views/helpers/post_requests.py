import logging

import cookie_booths.views.helpers as helpers
from cookie_booths.models import BoothTimeBlock, CookieSeason
from troops.models import Troop
from utils.display_message import MessageLoader

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

message_loader = MessageLoader()
error_messages = message_loader.load_error_messages()
success_messages = message_loader.load_success_messages()
warning_messages = message_loader.load_warning_messages()


def handle_post_request(request, block_id, action_func, daisy=False):
    block = BoothTimeBlock.objects.get(id=block_id)
    message, success = action_func(request, block, daisy)
    return helpers.message_response.create_message_response(
        message=message,
        is_success=success,
    )


def reserve_action(request, block_to_reserve, daisy):
    email = request.user.email
    user_identification = helpers.user_identification.identify_user(request, block_to_reserve)

    response = _check_user_identification(user_identification)
    if response:
        return response, False

    response = _check_ffa_and_tickets(user_identification, block_to_reserve)
    if response:
        return response, False

    booth = block_to_reserve.booth_day.booth
    troop_level = user_identification["troop_trying_to_reserve_level"]
    response = _check_troop_level_restrictions(booth, troop_level)
    if response:
        return response, False

    booth_day = block_to_reserve.booth_day.booth_day_date
    response = _check_booth_reservability(booth_day)
    if response:
        return response, False

    return _reserve_booth(block_to_reserve, user_identification, daisy, email)


def cancel_action(request, block_to_cancel, daisy):
    permission_message = _check_user_permissions(request, block_to_cancel, daisy)
    if permission_message:
        return permission_message, False

    if not daisy and block_to_cancel.cancel_block():
        return success_messages["cancelled_booth"], True
    elif daisy and block_to_cancel.cancel_daisy_reservation():
        return success_messages["cancelled_booth"], True
    else:
        return error_messages["failed_to_cancel_booth"], False


def _reserve_booth(block_to_reserve, user_identification, daisy, email):
    successful = False
    if daisy:
        successful = block_to_reserve.reserve_daisy_block(
            daisy_troop_id=user_identification["troop_trying_to_reserve"]
        )
    else:
        successful = block_to_reserve.reserve_block(
            troop_id=user_identification["troop_trying_to_reserve"],
            cookie_cap_id=user_identification["cookie_captain_id"],
        )
    if successful:
        message = _generate_success_message(user_identification, email)
    else:
        message = error_messages["failed_to_reserve_booth"]

    return helpers.message_response.create_message_response(
        message=message,
        is_success=successful,
    )


def _generate_success_message(user_identification, email):
    message_snippit = user_identification["troop_trying_to_reserve"]
    if user_identification["cookie_captain_id"]:
        message_snippit = email
    return success_messages["reserved_booth"].format(message_snippit=message_snippit)


def _check_troop_level_restrictions(booth, troop_level):
    if not booth.passes_level_restrictions(troop_level):
        return helpers.message_response.create_message_response(
            message=warning_messages["troop_restrictions"],
            is_success=False,
        )
    return None


def _check_booth_reservability(booth_day):
    if not CookieSeason.is_booth_reservable_for_date(booth_day):
        return helpers.message_response.create_message_response(
            message=warning_messages["booth_not_reservable"],
            is_success=False,
        )
    return None


def _check_ffa_and_tickets(user_identification, block_to_reserve):
    if not block_to_reserve.booth_day.booth_day_freeforall_enabled:
        return _check_tickets(user_identification, block_to_reserve)
    return None


def _check_user_identification(user_identification):
    if not user_identification["success"]:
        return helpers.message_response.create_message_response(
            message=user_identification["message"],
            is_success=user_identification["success"],
        )
    return None


def _check_tickets(user_identification, block_to_reserve):
    tickets_remain = user_identification["rem_tickets"]
    booth_is_golden = block_to_reserve.booth_day.booth_day_is_golden
    golden_tickets_remain = user_identification["rem_golden_tickets"]

    if not tickets_remain:
        return helpers.message_response.create_message_response(
            message="No remaining tickets for this week",
            is_success=False,
        )

    if booth_is_golden and not golden_tickets_remain:
        return helpers.message_response.create_message_response(
            message="No remaining golden tickets for this week",
            is_success=False,
        )
    return None


def _check_user_permissions(request, daisy, block_to_cancel):
    user_id = request.user.id
    email = request.user.email
    is_cookie_admin = request.user.has_perm("cookie_booths.block_reservation_admin")
    is_tcc = request.user.has_perm("cookie_booths.block_reservation")
    is_cookie_captain = request.user.has_perm("cookie_booths.cookie_captain_reserve_block")

    if is_cookie_admin:
        return None  # The user is a SUCM or higher they can do this unconditionally
    elif is_tcc:
        troop_trying_to_cancel = Troop.objects.get(troop_cookie_coordinator=email).troop_number
        if troop_trying_to_cancel != block_to_cancel.booth_block_current_troop_owner and (
            daisy and troop_trying_to_cancel != block_to_cancel.booth_block_daisy_troop_owner
        ):
            return warning_messages["cannot_cancel_for_another_troop"]
    elif is_cookie_captain:
        if block_to_cancel.booth_block_current_cookie_captain_owner != user_id:
            return warning_messages["cannot_cancel_for_another_troop"]
        elif block_to_cancel.booth_block_daisy_reserved:
            return warning_messages["cannot_cancel_daisy_reserved_booth"]
    else:
        return warning_messages["unexpected_user"]
    return None
