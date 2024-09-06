import logging
from enum import Enum

from accounts.models import CustomUser as User
from troops.models import Troop

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class PermissionLevel(Enum):
    NONE = "none"
    ADMIN = "admin"
    TCC = "tcc"
    DAISY = "daisy"


def get_permission_level(requestor: User) -> PermissionLevel:
    """
    Determines the permission level of a user.

    Args:
        requestor (User): The user for whom the permission level is being determined.

    Returns:
        PermissionLevel: The permission level of the user.
    """
    _logger.info("Determining user permission level.")
    permission_level = PermissionLevel.NONE
    if requestor.is_admin:
        permission_level = PermissionLevel.ADMIN
    elif requestor.is_tcc:
        if Troop.objects.is_daisy_troop_by_email(requestor.email):
            permission_level = PermissionLevel.DAISY
        else:
            permission_level = PermissionLevel.TCC
    elif requestor.is_cookie_captain:
        permission_level = PermissionLevel.TCC
    _logger.debug("User permission level: %s", permission_level)
    return permission_level


def can_hold_for_cookie_captains(user: User) -> bool:
    """
    Determine if the user can hold a booth for cookie captains.

    Args:
        user (User): The user object for which to determine if they can hold a booth.

    Returns:
        hold_for_cc: True if the user can hold a booth for cookie captains, False otherwise.
    """
    _logger.info("Checking if user can hold for cookie captains.")
    hold_for_cc = user.is_admin
    _logger.debug("Can the user hold for cookie captains? %s", hold_for_cc)
    return hold_for_cc
