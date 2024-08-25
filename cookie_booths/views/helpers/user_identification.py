import logging

from cookie_booths.models import BoothBlock, CookieSeason
from troops.models import Troop
from utils.display_message import MessageLoader

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

message_loader = MessageLoader()
error_messages = message_loader.load_error_messages()
success_messages = message_loader.load_success_messages()
warning_messages = message_loader.load_warning_messages()

DEFAULT_RESPONSE = {
    "troop_number": None,
    "troop_level": None,
    "rem_tickets": 0,
    "rem_golden_tickets": 0,
}


def identify_user(request, block_to_reserve):
    """
    Identifies the user and their permissions to reserve a block.

    Parameters:
    request (Request): The HTTP request object containing user information.
    block_to_reserve (Block): The block that the user is trying to reserve.

    Returns:
    dict: A dictionary containing the following keys:
        - success (bool): Whether the identification was successful.
        - message (str or None): A message indicating the result of the identification.
        - troop_trying_to_reserve (int): The troop number trying to reserve the block.
        - troop_trying_to_reserve_level (int): The level of the troop trying to reserve the block.
        - rem_tickets (int): The remaining tickets available for the troop.
        - rem_golden_tickets (int): The remaining golden tickets available for the troop.
        - cookie_captain_id (int or None): The ID of the cookie captain, if applicable.
    """
    user_identification = {
        "success": False,
        "message": None,
        "troop_trying_to_reserve": 0,
        "troop_trying_to_reserve_level": 0,
        "rem_tickets": 0,
        "rem_golden_tickets": 0,
        "cookie_captain_id": None,
    }

    if request.user.has_cookie_admin_permissions:
        troop_info = _identify_cookie_admin(request, block_to_reserve)
        if troop_info is None:
            user_identification["message"] = warning_messages["please_select_troop"]
            return user_identification
    elif request.user.has_tcc_permissions:
        troop_info = _identify_tcc(request, block_to_reserve)
    elif request.user.has_cookie_captain_permissions:
        user_identification["cookie_captain_id"] = request.user.id
        troop_info = _identify_cookie_captain(request, block_to_reserve)
    else:
        user_identification["message"] = error_messages["unexpected_user"]
        return user_identification

    user_identification.update(
        {
            "success": True,
            "troop_trying_to_reserve": troop_info["troop_number"],
            "troop_trying_to_reserve_level": troop_info["troop_level"],
            "rem_tickets": troop_info["rem_tickets"],
            "rem_golden_tickets": troop_info["rem_golden_tickets"],
        }
    )

    return user_identification


def get_owner_and_user_type(request):
    """
    Retrieves the owner and user type based on the given request.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        tuple: A tuple containing the owner and user type. The tuple has the following format:
            - owner: The troop number if it the user is a troop, or the user_id if cookie_captain.
            - is_daisy_troop: A boolean value indicating whether the user is part of a Daisy troop.
            - is_cookie_captain: A boolean value indicating whether the user is a cookie captain.
    """
    email = request.user.email
    user_id = request.user.id
    is_cookie_captain = request.user.has_cookie_captain_permissions

    user_troop = Troop.get_by_cookie_coordinator_email(email)
    if user_troop:
        return user_troop.troop_number, user_troop.is_daisy_troop, is_cookie_captain
    elif is_cookie_captain:
        return user_id, False, is_cookie_captain
    else:
        _logger.error("%s: %s", error_messages["unexpected_user"], email)
        return None, False, is_cookie_captain


def _get_cookie_captain_remaining_tickets(cookie_captain_id, date):
    total_booth_count = BoothBlock.objects.total_booth_count_for_cookie_captain(
        cookie_captain_id=cookie_captain_id,
        date=date,
    )

    # Cookie Captains cannot reserve during the first week of the season
    cookie_season = CookieSeason.objects.get(id=1)
    total_tickets = 3 if cookie_season.cookie_season_week(date) > 1 else 0

    return _calculate_remaining_tickets(
        total_tickets,
        total_booth_count,
    )


def _get_troop_remaining_tickets(troop_id: Troop, date):
    blocks_aggregated = BoothBlock.objects.aggregated_booth_count_for_troop(
        troop_id=troop_id,
        date=date,
    )

    total_booth_count = blocks_aggregated["total_booth_count"]
    golden_ticket_booth_count = blocks_aggregated["golden_ticket_booth_count"]

    total_tickets = troop_id.total_booth_tickets_per_week
    total_golden_tickets = troop_id.booth_golden_tickets_per_week

    return _calculate_remaining_tickets(
        total_tickets,
        total_booth_count,
        total_golden_tickets,
        golden_ticket_booth_count,
    )


def _calculate_remaining_tickets(
    total_tickets, total_booth_count, total_golden_tickets=0, total_golden_booth_count=0
):
    remaining_tickets = max(0, total_tickets - total_booth_count)
    remaining_golden_tickets = max(0, total_golden_tickets - total_golden_booth_count)

    return remaining_tickets, remaining_golden_tickets


def _get_num_tickets_remaining(troop_or_cookie_captain_id, date, is_cookie_captain=False):
    if is_cookie_captain:
        return _get_cookie_captain_remaining_tickets(troop_or_cookie_captain_id, date)
    else:
        return _get_troop_remaining_tickets(troop_or_cookie_captain_id, date)


def _get_troop_and_tickets(troop_number=None, email=None, block_to_reserve: BoothBlock = None):
    response = DEFAULT_RESPONSE.copy()

    if troop_number:
        troop = Troop.objects.get(troop_number=troop_number)
    elif email:
        troop = Troop.objects.get(troop_cookie_coordinator=email)
    else:
        troop = None

    if troop:
        rem_tickets, rem_golden_tickets = _get_num_tickets_remaining(
            troop_or_cookie_captain_id=troop,
            date=block_to_reserve.booth_day.booth_day_date,
        )
        response.update(
            {
                "troop_number": troop.troop_number,
                "troop_level": troop.troop_level,
                "rem_tickets": rem_tickets,
                "rem_golden_tickets": rem_golden_tickets,
            }
        )

    return response


def _get_cookie_captain_tickets(user_id, block_to_reserve):
    rem_tickets, rem_golden_tickets = _get_num_tickets_remaining(
        troop_or_cookie_captain_id=user_id,
        date=block_to_reserve.booth_day.booth_day_date,
        is_cookie_captain=True,
    )
    response = DEFAULT_RESPONSE.copy()
    response.update(
        {
            "rem_tickets": rem_tickets,
            "rem_golden_tickets": rem_golden_tickets,
        }
    )
    return response


def _identify_cookie_admin(request, block_to_reserve):
    troop_number = request.POST.get("troop_number")
    if not troop_number:
        return None
    return _get_troop_and_tickets(troop_number=troop_number, block_to_reserve=block_to_reserve)


def _identify_tcc(request, block_to_reserve):
    email = request.user.email
    return _get_troop_and_tickets(email=email, block_to_reserve=block_to_reserve)


def _identify_cookie_captain(request, block_to_reserve):
    return _get_cookie_captain_tickets(user_id=request.user.id, block_to_reserve=block_to_reserve)
