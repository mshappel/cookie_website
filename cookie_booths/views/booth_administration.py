from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import DeleteView

import cookie_booths.views.helpers as helpers
from cookie_booths.forms import BoothHoursForm, BoothLocationForm
from cookie_booths.models import BoothDay, BoothLocation, BoothSchedule
from utils.display_message import MessageLoader

message_loader = MessageLoader()
error_messages = message_loader.load_error_messages()
success_messages = message_loader.load_success_messages()
warning_messages = message_loader.load_warning_messages()


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
    booths = BoothLocation.objects.order_booth_locations()
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
        return helpers.form_helpers.handle_booth_form_submission(
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
        return helpers.form_helpers.handle_booth_form_submission(
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
    hours, _ = BoothSchedule.objects.get_or_create(booth_location=booth)
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
    booth_information = helpers.booth_helpers.get_booth_information()
    permission_level = helpers.permissions.get_permission_level(request.user)

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
    return helpers.toggles.handle_block_toggle(request, block_id, action="enable")


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
    return helpers.toggles.handle_block_toggle(request, block_id, action="disable")


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
    booth_days = BoothDay.objects.order_booth_days()

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
    return helpers.toggles.handle_day_toggle(request, action="enable")


@login_required
def disable_location_by_day(request):
    """
    Disables all dates for a particular booth up to and including a particular date.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    return helpers.toggles.handle_day_toggle(request, action="disable")
