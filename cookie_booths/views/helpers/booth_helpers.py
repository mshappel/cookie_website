import logging

from cookie_booths.models import BoothTimeBlock

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


def get_booth_information():
    """Fetch and construct booth information.

    This function retrieves booth information from the database and constructs a list
    of booth information dictionaries. Each dictionary contains the following keys:
    - booth_block_information: The booth block object.
    - booth_owned_by_current_user: Indicates whether the booth is owned by the current user.
    - booth_owned_by_cookie_captain: Indicates whether the booth is owned by a cookie captain.
    - booth_block_cookie_captain_email: The email address of the cookie captain for the booth block.

    Returns:
        A list of booth information dictionaries.
    """
    _logger.info("Fetching booth information")
    booth_information = []
    ordered_booth_blocks = BoothTimeBlock.objects.order_booth_blocks()

    for booth in ordered_booth_blocks:
        current_booth_information = {
            "booth_block_information": booth,
            "booth_owned_by_current_user": None,
            "booth_owned_by_cookie_captain": False,
            "booth_block_cookie_captain_email": "",
        }
        booth_information.append(current_booth_information)

    _logger.info("Booth information fetched successfully")
    _logger.debug("Booth information: %s", booth_information)
    return booth_information
