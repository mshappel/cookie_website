import logging

from django.http import HttpResponse

from cookie_booths.models import BoothDay, BoothTimeBlock

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


def handle_block_toggle(request, block_id, action):
    """
    Handles the toggle action for a booth block.

    Args:
        request (HttpRequest): The HTTP request object.
        block_id (int): The ID of the booth block.
        action (str): The action to perform (e.g., "toggle").

    Returns:
        HttpResponse: The HTTP response object.
    """
    return _handle_toggle(request, block_id, action, BoothTimeBlock, "block")


def handle_day_toggle(request, action):
    """
    Handles the toggle action for a specific booth on a specific day.

    Args:
        request (HttpRequest): The HTTP request object.
        action (str): The action to perform (e.g., "enable" or "disable").

    Returns:
        HttpResponse: The HTTP response object.

    """
    booth_id = request.POST["booth_id"]
    return _handle_toggle(request, booth_id, action, BoothDay, "day")


def _handle_toggle(request, obj_id, action, model_class, obj_type):
    """
    Handles the toggle action for a specific object.

    Args:
        request (HttpRequest): The HTTP request object.
        obj_id (int): The ID of the object to toggle.
        action (str): The action to perform (either "enable" or "disable").
        model_class (class): The class of the model for the object.
        obj_type (str): The type of the object.

    Returns:
        HttpResponse: The HTTP response indicating the success of the toggle action.
    """
    is_success = False
    if request.method == "POST":
        obj_to_modify = model_class.objects.get(id=obj_id)
        if request.user.has_perm("cookie_booths.toggle_day"):
            if action == "enable":
                is_success = getattr(obj_to_modify, f"enable_{obj_type}")()
            elif action == "disable":
                is_success = getattr(obj_to_modify, f"disable_{obj_type}")()

    return HttpResponse(is_success)
