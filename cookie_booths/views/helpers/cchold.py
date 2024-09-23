import logging

from django.shortcuts import get_object_or_404

from cookie_booths.models import BoothTimeBlock
from cookie_booths.views.helpers.message_response import create_message_response
from cookie_booths.views.helpers.permissions import can_hold_for_cookie_captains
from utils.display_message import MessageLoader

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

message_loader = MessageLoader()
error_messages = message_loader.load_error_messages()
success_messages = message_loader.load_success_messages()
warning_messages = message_loader.load_warning_messages()


def process_block_action(request, block_id, action):
    """
    Process the action for a booth block.
    Args:
        request: The request object.
        block_id: The ID of the booth block.
        action: The action to be performed.
    Returns:
        The result of the block action.
    """
    block = _get_booth_block(request, block_id)
    if block is None:
        return create_message_response(warning_messages["wrong_permissions"], False)

    if action == "hold":
        condition = (
            not block.booth_block_held_for_cookie_captains and not block.booth_block_reserved
        )
        success_message = success_messages["held_booth"].format(message_snippit="cookie captains")
        warning_message = warning_messages["booth_cannot_be_reserved"]
    elif action == "unhold":
        condition = block.booth_block_held_for_cookie_captains
        success_message = success_messages["unheld_booth"]
        warning_message = warning_messages["booth_not_held"]
    else:
        return _log_and_create_error_message(action=action)

    return _block_action_for_cookie_captain(
        condition,
        block,
        success_message,
        warning_message,
        action,
    )


def _block_action_for_cookie_captain(
    condition, block: BoothTimeBlock, success_message, warning_message, action
):
    if condition:
        if action == "hold":
            block.hold_for_cookie_captains()
            return create_message_response(success_message, True)
        elif action == "unhold":
            block.unhold_for_cookie_captains()
            return create_message_response(success_message, True)
        else:
            _logger.error("Invalid action for cookie captain block action")
    else:
        return create_message_response(warning_message, False)


def _get_booth_block(request, block_id):
    if can_hold_for_cookie_captains(request.user):
        block = get_object_or_404(BoothTimeBlock, id=block_id)
    else:
        block = None
    return block


def _log_and_create_error_message(action):
    error_message: str = error_messages["invalid_action"]
    display_message = error_message.format(message_snippit=action)
    _logger.error(display_message)
    return create_message_response(display_message, False)
