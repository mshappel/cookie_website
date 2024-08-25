import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.timezone import datetime, make_aware, timedelta

import cookie_booths.views.helpers as helpers
from utils.display_message import MessageLoader

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

message_loader = MessageLoader()
error_messages = message_loader.load_error_messages()
success_messages = message_loader.load_success_messages()
warning_messages = message_loader.load_warning_messages()


@login_required
def booth_blocks(request):
    time_threshold = make_aware(datetime.today()) - timedelta(hours=6, minutes=30)
    return helpers.renders.render_booth_view(
        request=request,
        time_threshold=time_threshold,
        page_title="Make Booth Reservations",
        reserve_or_enable_booths="reserve",
    )


@login_required
def booth_reservations(request):
    return helpers.renders.render_booth_view(
        request=request,
        time_threshold=None,
        page_title="Make Booth Reservations",
        reserve_or_enable_booths="reserve",
    )


@login_required
def reserve_block(request, daisy, block_id):
    if request.method == "POST":
        return helpers.post_requests.handle_post_request(
            request=request,
            block_id=block_id,
            action_func=helpers.post_requests.reserve_action,
            daisy=daisy,
        )
    return JsonResponse({"message": None, "is_success": False})


@login_required
def cancel_block(request, daisy, block_id):
    if request.method == "POST":
        return helpers.post_requests.handle_post_request(
            request=request,
            block_id=block_id,
            action_func=helpers.post_requests.cancel_action,
            daisy=daisy,
        )
    return helpers.message_response.create_message_response(
        message=error_messages["unknown_issue"],
        is_success=False,
    )


@login_required
def hold_block_for_cookie_captain(request, block_id):
    return helpers.cchold.process_block_action(request, block_id, "hold")


@login_required
def cancel_hold_for_cookie_captain(request, block_id):
    return helpers.cchold.process_block_action(request, block_id, "unhold")
