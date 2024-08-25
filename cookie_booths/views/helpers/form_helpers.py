from typing import Optional

from django.contrib import messages
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from cookie_booths.models import BoothBlock
from utils.display_message import MessageLoader

message_loader = MessageLoader()
error_messages = message_loader.load_error_messages()
success_messages = message_loader.load_success_messages()
warning_messages = message_loader.load_warning_messages()


def handle_booth_form_submission(
    request: HttpRequest,
    form: ModelForm,
    success_redirect: str,
    template_name: str,
    booth: Optional[BoothBlock] = None,
) -> HttpResponse:
    """
    Handles the submission of a booth form.

    Args:
        request (HttpRequest): The HTTP request object.
        form (ModelForm): The form object to be validated and saved.
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
