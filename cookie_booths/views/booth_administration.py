from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import DeleteView

from cookie_booths.forms import BoothHoursForm, BoothLocationForm
from cookie_booths.models import BoothBlock, BoothDay, BoothHours, BoothLocation
from cookie_booths.views.helpers import get_permission_level
from utils.display_message import load_error_messages

error_messages = load_error_messages()


@login_required
def booth_editor(request):
    """
    Display all booths for admins to edit.

    This view function retrieves all booth locations from the database and
    orders them by their location. It then renders the 'booths.html' template
    with the retrieved booth locations as the context.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.
    """
    booths = BoothLocation.objects.order_by("booth_location")
    context = {"booths": booths}
    return render(request, "cookie_booths/booths.html", context)


@login_required
@permission_required("cookie_booths.add_boothlocation", raise_exception=True)
def create_new_booth_location(request):
    """
    Create a new booth location.

    This view function is responsible for creating a new booth location. It requires the user to be
    logged in and have the permission to add a booth location.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - If the request method is POST and the form is valid, it saves the booth location and redirects
      to the edit booth hours page for the newly created booth location.
    - If there is an exception while saving the booth location, it adds an error message to the
      form and renders the new booth location page again.
    - If the request method is GET or the form is not valid, it renders the new booth location page
      with the form.

    """
    form = BoothLocationForm(request.POST or None)
    if request.method == "POST":
        return handle_form_submission(
            request=request,
            form=form,
            success_redirect="cookie_booths:edit_booth_hours",
            template_name="new_booth_location.html",
        )
    context = {"form": form}
    return render(request, "cookie_booths/new_booth_location.html", context)


@login_required
@permission_required("cookie_booths.change_boothlocation", raise_exception=True)
def edit_booth_location(request, booth_id):
    """
    Edit an existing booth location.

    Args:
        request: The HTTP request object.
        booth_id: The ID of the booth location to be edited.

    Returns:
        A rendered HTML template for editing the booth location.
    """
    booth = get_object_or_404(BoothLocation, id=booth_id)
    form = BoothLocationForm(instance=booth, data=request.POST or None, booth_id=booth_id)
    if request.method == "POST":
        return handle_form_submission(
            request=request,
            form=form,
            success_redirect="cookie_booths:booth_locations",
            template_name="edit_booth.html",
            booth=booth,
        )
    context = {"booth": booth, "form": form}
    return render(request, "cookie_booths/edit_booth.html", context)


@login_required
@permission_required("cookie_booths.change_boothlocation", raise_exception=True)
def edit_booth_location_hours(request, booth_id):
    """
    Edit an existing booth location.

    Args:
        request (HttpRequest): The HTTP request object.
        booth_id (int): The ID of the booth location to be edited.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        Http404: If the booth location with the given ID does not exist.

    """
    booth = get_object_or_404(BoothLocation, id=booth_id)
    hours, _ = BoothHours.objects.get_or_create(booth_location=booth)
    form = BoothHoursForm(instance=hours, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(reverse("cookie_booths:booth_locations"))

    context = {"booth": booth, "form": form}
    return render(request, "cookie_booths/edit_booth_hours.html", context)


class BoothLocationDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    """
    View to delete an existing booth location.

    This view handles the deletion of a booth location. It ensures that the user
    has the necessary permissions and is authenticated before allowing the deletion.

    Attributes:
        permission_required (str): The permission required to delete a booth location.
        model (Model): The model representing the booth location to be deleted.
        template_name (str): The template used to confirm the deletion.
        success_url (str): The URL to redirect to upon successful deletion.
    """

    permission_required = "cookie_booths.delete_boothlocation"
    model = BoothLocation
    template_name = "cookie_booths/booth_confirm_delete.html"
    success_url = reverse_lazy("cookie_booths:booth_locations")


@login_required
@permission_required("cookie_booths.toggle_day", raise_exception=True)
def enable_location_by_block(request):
    """
    Enables the booths by block for the cookie booth administration.

    This view function is responsible for rendering the booth_blocks.html template
    and passing the necessary data to the template context. It requires the user to be
    logged in and have the "cookie_booths.toggle_day" permission.

    Returns:
        A rendered HTTP response with the booth_blocks.html template and the context data.
    """
    booth_information = get_booth_information()
    permission_level = get_permission_level(request.user)

    context = {
        "booth_blocks": booth_information,
        "available_troops": None,
        "permission_level": permission_level,
        "page_title": "Enable Booths by Block",
        "reserve_or_enable_booths": "enable",
    }

    return render(request, "cookie_booths/booth_blocks.html", context)


@login_required
def ajax_enable_location_by_block(request, block_id):
    """
    Enable a location by block ID using AJAX.

    Args:
        request (HttpRequest): The HTTP request object.
        block_id (int): The ID of the block.

    Returns:
        HttpResponse: The HTTP response object.
    """
    return handle_block_toggle(request, block_id, action="enable")


@login_required
def ajax_disable_location_by_block(request, block_id):
    """
    Disables a location by block ID.

    Args:
        request (HttpRequest): The HTTP request object.
        block_id (int): The ID of the block to disable.

    Returns:
        HttpResponse: The HTTP response object.
    """
    return handle_block_toggle(request, block_id, action="disable")


@login_required
@permission_required("cookie_booths.toggle_day", raise_exception=True)
def enable_or_disable_day(request):
    """
    View function to enable or disable booth days.

    This function is responsible for rendering the "Enable/Disable Booth Days" page
    and handling the logic to enable or disable booth days based on user permissions.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered template.

    Raises:
        PermissionDenied: If the user does not have the required permission.

    """
    booth_days = BoothDay.objects.order_by("booth", "booth_day_date")

    context = {
        "booth_days": booth_days,
        "page_title": "Enable/Disable Booth Days",
    }

    return render(request, "cookie_booths/enable_blocks.html", context)


@login_required
def enable_location_by_day(request):
    """
    Enable all dates for a particular booth up to and including a particular date.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    return handle_day_toggle(request, action="enable")


@login_required
def disable_location_by_day(request):
    """
    Disables all dates for a particular booth up to and including a particular date.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    return handle_day_toggle(request, action="disable")


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
    booth_information = []
    booth_blocks_ = BoothBlock.objects.order_by(
        "booth_day__booth", "booth_day", "booth_block_start_time"
    ).select_related("booth_day", "booth_day__booth")

    for booth in booth_blocks_:
        current_booth_information = {
            "booth_block_information": booth,
            "booth_owned_by_current_user": None,
            "booth_owned_by_cookie_captain": False,
            "booth_block_cookie_captain_email": "",
        }
        booth_information.append(current_booth_information)

    return booth_information


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
    return handle_toggle(request, block_id, action, BoothBlock, "block")


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
    return handle_toggle(request, booth_id, action, BoothDay, "day")


def handle_toggle(request, obj_id, action, model_class, obj_type):
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


def handle_form_submission(request, form, success_redirect, template_name, booth=None):
    """
    Handles the submission of a form.

    Args:
        request (HttpRequest): The HTTP request object.
        form (Form): The form object to be validated and saved.
        success_redirect (str): The URL to redirect to upon successful form submission.
        template_name (str): The name of the template to render.
        booth (object, optional): The booth object associated with the form (default: None).

    Returns:
        HttpResponse: The HTTP response object.

    """
    if form.is_valid():
        try:
            loc = form.save()
            if booth:
                return HttpResponseRedirect(reverse_lazy(success_redirect))
            return redirect(success_redirect, booth_id=loc.id)
        except Exception as e:
            error_message = error_messages["save_booth_location"].format(error=e)
            form.add_error(None, error_message)
            messages.error(request, error_message)
    else:
        error_message = error_messages["generic_form_error"]
        messages.error(request, error_message)
    context = {"form": form}
    if booth:
        context["booth"] = booth
    return render(request, f"cookie_booths/{template_name}", context)
