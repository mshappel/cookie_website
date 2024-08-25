import logging

from django.http import HttpResponse
from django.shortcuts import render

from cookie_booths.views.helpers.context import get_booth_context

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


def render_booth_view(request, time_threshold, page_title, reserve_or_enable_booths):
    context = get_booth_context(request, time_threshold)
    if isinstance(context, HttpResponse):
        return context

    context["page_title"] = page_title
    context["reserve_or_enable_booths"] = reserve_or_enable_booths

    return render(request, "cookie_booths/booth_blocks.html", context)
