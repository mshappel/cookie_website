import logging

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


def get_permission_level(user, is_daisy_troop=False, is_cookie_captain=False):
    """
    Determine the permission level of the user.

    Args:
        user (User): The user object for which to determine the permission level.
        is_daisy_troop (bool): Whether the user is part of a Daisy troop.
        is_cookie_captain (bool): Whether the user is a cookie captain.

    Returns:
        str: The permission level of the user. Possible values are "admin", "tcc", "daisy", or "none".
    """
    permission_level = "none"
    if user.has_cookie_admin_permissions:
        permission_level = "admin"
    elif user.has_tcc_permissions:
        if is_daisy_troop:
            permission_level = "daisy"
        else:
            permission_level = "tcc"
    elif is_cookie_captain:
        permission_level = "tcc"
    return permission_level


def can_hold_for_cookie_captains(user):
    """
    Determine if the user can hold a booth for cookie captains.

    Args:
        user (User): The user object for which to determine if they can hold a booth.

    Returns:
        bool: True if the user can hold a booth for cookie captains, False otherwise.
    """
    return user.has_cookie_admin_permissions
