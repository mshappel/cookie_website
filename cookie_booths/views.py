from datetime import timedelta, datetime
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from cookie_website.settings import NO_COOKIE_CAPTAIN_ID

from .forms import BoothLocationForm, BoothHoursForm, EnableFreeForAll
from .models import BoothLocation, BoothDay, BoothHours, BoothBlock, CookieSeason
from troops.models import Troop

# -----------------------------------------------------------------------
# Booth Admin Functions
# -----------------------------------------------------------------------


@login_required
def booth_editor(request):
    """Display all booths for admins to edit"""
    booths = BoothLocation.objects.order_by("booth_location")
    context = {"booths": booths}
    return render(request, "cookie_booths/booths.html", context)


@login_required
@permission_required("cookie_booths.add_boothlocation", raise_exception=True)
def create_new_booth_location(request):
    """Create a new booth location"""
    if request.method != "POST":
        # No data submitted; create a blank form.
        form = BoothLocationForm()
    else:
        # POST data submitted; process data.
        form = BoothLocationForm(data=request.POST)
        if form.is_valid():
            loc = form.save()
            return redirect("cookie_booths:edit_booth_hours", booth_id=loc.id)

    # Display a blank or invalid form.
    context = {"form": form}
    return render(request, "cookie_booths/new_booth_location.html", context)


@login_required
@permission_required("cookie_booths.change_boothlocation", raise_exception=True)
def edit_booth_location(request, booth_id):
    """Edit an existing booth location"""
    booth = BoothLocation.objects.get(id=booth_id)

    if request.method != "POST":
        # Initial request; pre-fill with the current entry.
        form = BoothLocationForm(instance=booth, booth_id=booth_id)
    else:
        # POST data submitted; process data.
        form = BoothLocationForm(instance=booth, data=request.POST, booth_id=booth_id)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy("cookie_booths:booth_locations"))

    context = {"booth": booth, "form": form}
    return render(request, "cookie_booths/edit_booth.html", context)


@login_required
@permission_required("cookie_booths.change_boothlocation", raise_exception=True)
def edit_booth_location_hours(request, booth_id):
    """Edit an existing booth location"""
    booth = BoothLocation.objects.get(id=booth_id)
    hours = BoothHours.objects.get(booth_location=booth.id)

    if request.method != "POST":
        # Initial request; pre-fill with the current entry.
        form = BoothHoursForm(instance=hours)
    else:
        # POST data submitted; process data.
        form = BoothHoursForm(instance=hours, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy("cookie_booths:booth_locations"))

    context = {"booth": booth, "form": form}
    return render(request, "cookie_booths/edit_booth_hours.html", context)


class BoothLocationDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    """Delete an existing booth location"""

    permission_required = "cookie_booths.delete_boothlocation"
    model = BoothLocation
    template_name = "cookie_booths/booth_confirm_delete.html"
    success_url = reverse_lazy("cookie_booths:booth_locations")


@login_required
@permission_required("cookie_booths.toggle_day", raise_exception=True)
def enable_location_by_block(request):
    booth_information = []
    booth_blocks_ = BoothBlock.objects.order_by(
        "booth_day__booth", "booth_day", "booth_block_start_time"
    )

    for booth in booth_blocks_:
        current_booth_information = {
            "booth_block_information": booth,
            "booth_owned_by_current_user": None,
        }
        booth_information.append(current_booth_information)

    permission_level = "none"
    if request.user.has_perm("cookie_booths.block_reservation_admin"):
        permission_level = "admin"
    elif request.user.has_perm("cookie_booths.block_reservation"):
        permission_level = "tcc"

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
    is_success = False
    if request.method == "POST":
        block_to_enable = BoothBlock.objects.get(id=block_id)
        if request.user.has_perm("cookie_booths.toggle_day"):
            is_success = block_to_enable.enable_block()

    return HttpResponse(is_success)


@login_required
def ajax_disable_location_by_block(request, block_id):
    is_success = False
    if request.method == "POST":
        block_to_enable = BoothBlock.objects.get(id=block_id)
        if request.user.has_perm("cookie_booths.toggle_day"):
            is_success = block_to_enable.disable_block()

    return HttpResponse(is_success)


@login_required
@permission_required("cookie_booths.toggle_day", raise_exception=True)
def enable_or_disable_day(request):
    booth_days = BoothDay.objects.order_by("booth", "booth_day_date")

    context = {
        "booth_days": booth_days,
        "page_title": "Enable/Disable Booth Days",
    }

    return render(request, "cookie_booths/enable_blocks.html", context)


@login_required
def enable_location_by_day(request):
    # Enable all dates for a particular booth up to and including a particular date
    if request.method == "POST":
        booth_id = request.POST["booth_id"]
        booth_day = BoothDay.objects.get(id=booth_id)
        if request.user.has_perm("cookie_booths.toggle_day"):
            booth_day.enable_day()

    return HttpResponse()


@login_required
def disable_location_by_day(request):
    # Disable all dates for a particular booth up to and including a particular date
    if request.method == "POST":
        booth_id = request.POST["booth_id"]
        booth_day = BoothDay.objects.get(id=booth_id)
        if request.user.has_perm("cookie_booths.toggle_day"):
            booth_day.disable_day()

    return HttpResponse()


@login_required
def enable_location_ffa(request, booth_id, date):
    # Enable free-for-all for a particular booth up to and including a particular date.
    # Will also enable dates up until that day if not already
    for booth_day in BoothDay.objects.filter(
        booth_id=booth_id, booth_day_date__lte=date
    ):
        booth_day.enable_freeforall()

    return


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


@login_required
def enable_all_locations_ffa(request):
    # Enable free-for-all for all locations up to and including a particular date.
    # Will also enable those dates if not already
    """Create a new booth location"""
    if request.method != "POST":
        # No data submitted; create a blank form.
        form = EnableFreeForAll()
    else:
        # POST data submitted; process data.
        form = EnableFreeForAll(data=request.POST)
        if form.is_valid():
            start_date = datetime.strptime(request.POST["start_date"], "%m/%d/%Y")
            end_date = datetime.strptime(request.POST["end_date"], "%m/%d/%Y")
            for date_ in daterange(start_date, end_date):
                for booth_day in BoothDay.objects.filter(booth_day_date=date_):
                    booth_day.enable_freeforall()

            return HttpResponse("Complete")

    # Display a blank or invalid form.
    context = {"form": form}

    return render(request, "cookie_booths/free_for_all.html", context)


# -----------------------------------------------------------------------
# Booth User Functions
# -----------------------------------------------------------------------


@login_required
def booth_blocks(request):
    """Display all booths"""
    booth_blocks_ = BoothBlock.objects.order_by(
        "booth_day__booth", "booth_day", "booth_block_start_time"
    )
    available_troops = Troop.objects.order_by("troop_number")
    email = request.user.email
    booth_information = []

    try:
        user_troop = Troop.objects.get(troop_cookie_coordinator=email)
    except Troop.DoesNotExist:
        user_troop = None

    # Booth filtering step
    # 1. Disabled Booths should be excluded for everyone
    booth_blocks_ = booth_blocks_.exclude(booth_block_enabled=False)
    # 2. If the active user belongs to a Daisy Troop, they should ONLY be able to see booths that are reserved by
    # Cookie Captains
    if user_troop is not None and user_troop.troop_level == 1:
        booth_blocks_ = booth_blocks_.exclude(booth_block_current_cookie_captain_owner=NO_COOKIE_CAPTAIN_ID)
    # 3. If the user is not a Cookie Captain, they should not be able to see those booths
    elif not request.user.has_perm('cookie_booths.cookie_captain_reserve_block'):
        booth_blocks_ = booth_blocks_.exclude(booth_block_held_for_cookie_captains=True)


    for booth in booth_blocks_:
        if user_troop is None:
            booth_owned_by_current_user_ = False
        else:
            if booth.booth_block_current_troop_owner == user_troop.troop_number or \
               booth.booth_block_daisy_troop_owner == user_troop.troop_number:
                booth_owned_by_current_user_ = True
            else:
                booth_owned_by_current_user_ = False
        current_booth_information = {
            "booth_block_information": booth,
            "booth_owned_by_current_user": booth_owned_by_current_user_,
        }
        booth_information.append(current_booth_information)

    permission_level = "none"
    if request.user.has_perm("cookie_booths.block_reservation_admin"):
        permission_level = "admin"
    elif request.user.has_perm("cookie_booths.block_reservation"):
        if user_troop is not None and user_troop.troop_level==1:
            permission_level = "daisy"
        else:
            permission_level = "tcc"

    context = {
        "booth_blocks": booth_information,
        "available_troops": available_troops,
        "permission_level": permission_level,
        "page_title": "Make Booth Reservations",
        "reserve_or_enable_booths": "reserve",
    }

    return render(request, "cookie_booths/booth_blocks.html", context)


@login_required
def booth_reservations(request):
    """Display all blocks currently reserved by the current user"""
    booth_blocks_ = BoothBlock.objects.order_by(
        "booth_day__booth", "booth_day", "booth_block_start_time"
    )
    booth_blocks_ = booth_blocks_.exclude(booth_block_enabled=False)
    available_troops = Troop.objects.order_by("troop_number")
    email = request.user.email
    booth_information = []

    try:
        user_troop = Troop.objects.get(troop_cookie_coordinator=email)
        if user_troop.troop_level==1:
            booth_blocks_ = booth_blocks_.filter(
                booth_block_daisy_troop_owner=user_troop.troop_number
            )
        else:
            booth_blocks_ = booth_blocks_.filter(
                booth_block_current_troop_owner=user_troop.troop_number
            )
    except Troop.DoesNotExist:
        user_troop = None

    for booth in booth_blocks_:
        if user_troop is None:
            booth_owned_by_current_user_ = False
        else:
            if booth.booth_block_current_troop_owner == user_troop.troop_number or \
               booth.booth_block_daisy_troop_owner == user_troop.troop_number:
                booth_owned_by_current_user_ = True
            else:
                booth_owned_by_current_user_ = False
        current_booth_information = {
            "booth_block_information": booth,
            "booth_owned_by_current_user": booth_owned_by_current_user_,
        }
        booth_information.append(current_booth_information)

    permission_level = "none"
    if request.user.has_perm("cookie_booths.block_reservation_admin"):
        permission_level = "admin"
    elif request.user.has_perm("cookie_booths.block_reservation"):
        if user_troop is not None and user_troop.troop_level==1:
            permission_level = "daisy"
        else:
            permission_level = "tcc"

    context = {
        "booth_blocks": booth_information,
        "available_troops": available_troops,
        "permission_level": permission_level,
        "page_title": "Manage Your Booth Reservations",
        "reserve_or_enable_booths": "reserve",
    }

    return render(request, "cookie_booths/booth_blocks.html", context)


@login_required
def get_available_dates(request):
    # Go through all booth locations, and based on an intersection of those, figure out the list of available
    # Dates for selecting blocks
    return


@login_required
def get_available_blocks(request, date):
    # Go through all booth locations open on a particular date, and return all of the blocks,
    # Probably ordered and grouped by location in some kind of (location/location_name, [block list]) tuple format
    return


@login_required
def is_block_enabled(request, block_id):
    # Check if block is enabled for reservation. May still be cancelable
    return


@login_required
def is_block_reserved(request, block_id):
    # Check if block is reserved by a user that is *not* the current user
    return


@login_required
def is_block_reserved_by_user(request, block_id):
    # Check if block is reserved by the current user, and thus can be cancelled
    return


def get_week_start_end_from_date(date):
    start_date = date - timedelta(days=date.weekday())
    end_date = start_date + timedelta(days=6)

    return start_date, end_date


def get_num_tickets_remaining_cookie_captain(cookie_captain_id, date):
    start_date, end_date = get_week_start_end_from_date(date)

    total_booth_count = 0
    # We're filtering by Blocks that are owned by this troop, and are associated with a BoothDay which falls into
    # the range of [start_date, end_date] inclusive
    blocks_ = BoothBlock.objects.filter(
        booth_block_reserved=True,
        booth_day__booth_day_date__gte=start_date,
        booth_day__booth_day_date__lte=end_date,
    )

    blocks_ = blocks_.filter(booth_block_current_cookie_captain_owner=cookie_captain_id)
    total_booth_count = blocks_.count()

    # In the future, we need to fix the cookie seasons to the booth locations, but I don't want to
    # in the middle of the season and potentially mess stuff up, so here we are using id 1
    # Cookie Captains cannot reserve during the first week of the season
    cookie_captain_total_booth = 0
    if CookieSeason.objects.get(id=1).cookie_season_week(date) > 1:
        cookie_captain_total_booth = 3

    rem = (
        0
        if (total_booth_count > cookie_captain_total_booth)
        else (cookie_captain_total_booth - total_booth_count)
    )
    rem_golden_ticket = 0

    return rem, rem_golden_ticket

def get_num_tickets_remaining(troop, date):
    start_date, end_date = get_week_start_end_from_date(date)

    total_booth_count = 0
    golden_ticket_booth_count = 0
    # We're filtering by Blocks that are owned by this troop, and are associated with a BoothDay which falls into
    # the range of [start_date, end_date] inclusive
    blocks_ = BoothBlock.objects.filter(
        booth_block_reserved=True,
        booth_day__booth_day_date__gte=start_date,
        booth_day__booth_day_date__lte=end_date,
    )

    # If this is a daisy troop, they cannot be the primary owner of a block, only secondary
    # So we need to filter them differently based on that
    if troop.troop_level==1:
        blocks_ = blocks_.filter(booth_block_daisy_troop_owner=troop.troop_number)
    else:
        blocks_ = blocks_.filter(booth_block_current_troop_owner=troop.troop_number)

    for block in blocks_:
        if block.booth_day.booth_day_is_golden:
            golden_ticket_booth_count += 1

        total_booth_count += 1

    rem = (
        0
        if (total_booth_count > troop.total_booth_tickets_per_week)
        else (troop.total_booth_tickets_per_week - total_booth_count)
    )
    rem_golden_ticket = (
        0
        if (golden_ticket_booth_count > troop.booth_golden_tickets_per_week)
        else (troop.booth_golden_tickets_per_week - golden_ticket_booth_count)
    )

    return rem, rem_golden_ticket


@login_required
def reserve_block(request, daisy, block_id):
    # Cookie Captains can reserve any booth that has a) been reserved for them by the admin or
    # b) available to any other troop
    # Non-Daisy Troops can reserve any booth that isn't already reserved by a CC or troop
    # Daisy Troops can only reserve booths that have already been reserved by a CC.
    
    # Attempt to reserve a block, based on the amount of tickets available to the user, FFA status, etc
    email = request.user.email
    message_response = {}

    # A few items to gather for sending an email down below - whether the cancel was successful, whether it was
    # Cancelled by the troop that made it or by an admin, and the email address of the TCC who owns that block
    successful = False
    block_to_reserve = BoothBlock.objects.get(id=block_id)
    troop = None
    cookie_captain_id = settings.NO_COOKIE_CAPTAIN_ID

    if request.method == "POST":
        if request.user.has_perm("cookie_booths.block_reservation_admin"):
            # The user is a SUCM or higher; we require a troop # from them for reservation
            troop_trying_to_reserve = request.POST["troop_number"]
            if troop_trying_to_reserve == "":
                message_response = {
                    "message": "Please select a troop",
                    "is_success": False,
                }
                message_response = json.dumps(message_response)
                return HttpResponse(message_response)

            troop = Troop.objects.get(troop_number=troop_trying_to_reserve)
            troop_trying_to_reserve_level = troop.troop_level
            rem_tickets, rem_golden_tickets = get_num_tickets_remaining(
                troop, block_to_reserve.booth_day.booth_day_date
            )

        elif request.user.has_perm("cookie_booths.block_reservation"):
            # The user is a TCC; the user's troop # is used for reservation
            troop = Troop.objects.get(troop_cookie_coordinator=email)
            troop_trying_to_reserve = troop.troop_number
            troop_trying_to_reserve_level = troop.troop_level
            rem_tickets, rem_golden_tickets = get_num_tickets_remaining(
                troop, block_to_reserve.booth_day.booth_day_date
            )

        elif request.user.has_perm("cookie_booths.cookie_captain_reserve_block"):
            cookie_captain_id = request.user.id
            rem_tickets, rem_golden_tickets = get_num_tickets_remaining_cookie_captain(
                cookie_captain_id, block_to_reserve.booth_day.booth_day_date
            )
            troop_trying_to_reserve = 0
            troop_trying_to_reserve_level = settings.

        else:
            # The user does not have the permissions to reserve a block
            # This should never occur, but adding this in the case something horribly goes wrong.
            return

        # Check if the troop has remaining tickets for the week
        tickets_remain = True
        if rem_tickets == 0:
            message_response = {
                "message": "No remaining tickets for this week",
                "is_success": False,
            }
            tickets_remain = False

        # Tickets may remain, but check to see if they may have a golden booth.
        if block_to_reserve.booth_day.booth_day_is_golden and rem_golden_tickets == 0:
            message_response = {
                "message": "No remaining golden tickets for this week",
                "is_success": False,
            }
            tickets_remain = False

        # I am not interested in making a real solution today. Fix this later screw it
        if block_to_reserve.booth_day.booth_day_freeforall_enabled:
            tickets_remain = True

        if not tickets_remain:
            # We have no more remaining tickets, alert the user.
            message_response = json.dumps(message_response)
            return HttpResponse(message_response)

        # Check if the troop is a valid troop level
        booth_restrictions_start = (
            block_to_reserve.booth_day.booth.booth_block_level_restrictions_start
        )
        booth_restrictions_end = (
            block_to_reserve.booth_day.booth.booth_block_level_restrictions_end
        )

        if booth_restrictions_start == 0:
            level_in_range = True
        else:
            level_in_range = troop_trying_to_reserve_level in range(
                booth_restrictions_start, booth_restrictions_end + 1
            )

        if level_in_range:
            # If this is for a daisy troop, we need to reserve the block differently
            if not daisy and \
                block_to_reserve.reserve_block(troop_id=troop_trying_to_reserve, 
                                               cookie_cap_id=cookie_captain_id):
                # Successfully reserved the booth
                successful = True
                message_response = {
                    "message": f"Successfully reserved booth for {troop_trying_to_reserve}",
                    "is_success": True,
                }
            elif daisy and \
                block_to_reserve.reserve_daisy_block(daisy_troop_id=troop_trying_to_reserve):
                # Successfully reserved the booth
                successful = True
                message_response = {
                    "message": "Successfully reserved booth",
                    "is_success": True,
                }
            else:
                message_response = {
                    "message": "Failed to reserve booth",
                    "is_success": False,
                }
                
        else:
            message_response = {
                "message": "Booth has troop level restriction",
                "is_success": False,
            }
    else:
        message_response = {
            "message": "An unknown error occurred",
            "is_success": False,
        }

    # In the case this block has been reserved for a daisy troop, the TCC needs to be notified
    new_block_owner = "test@test.com"
    if successful and new_block_owner and troop.troop_level == 1:
        # First we should see if we were actually able to get an email we're sending to.
        # TODO: This should be a template
        title = "Booth Reservation Confirmed"
        message = (
            "Hello "
            + new_block_owner
            + ",\n"
            + "The following reservation has been made for Daisy Troop #"
            + troop.troop_number.__str__()
            + ":\n\n"
            + "Location: "
            + block_to_reserve.booth_day.booth.booth_location
            + "\n"
            + "Address: "
            + block_to_reserve.booth_day.booth.booth_address
            + "\n"
            + "Date: "
            + block_to_reserve.booth_day.booth_day_date.strftime("%A, %B %d, %Y")
            + "\n"
            + "Time Block: "
            + block_to_reserve.booth_block_start_time.strftime("%I:%M %p")
            + " - "
            + block_to_reserve.booth_block_end_time.strftime("%I:%M %p")
            + "\n\n\n"
            + "NOTE: Please do not reply to this email directly, this email address is not monitored. Please "
            "reach out to an administrator with any further questions. "
        )

        send_mail(
            title,
            message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[new_block_owner],
        )

    message_response = json.dumps(message_response)
    return HttpResponse(message_response)

@login_required
def cancel_block(request, daisy, block_id):
    email = request.user.email

    if request.method == "POST":
        block_to_cancel = BoothBlock.objects.get(id=block_id)
        if request.user.has_perm("cookie_booths.block_reservation_admin"):
            # The user is a SUCM or higher they can do this unconditionally
            pass
        elif request.user.has_perm("cookie_booths.block_reservation"):
            # The user is a TCC; the user's troop # is used to check if they can cancel
            troop_trying_to_cancel = Troop.objects.get(troop_cookie_coordinator=email).troop_number
            if (troop_trying_to_cancel != block_to_cancel.booth_block_current_troop_owner and
                (daisy and troop_trying_to_cancel != block_to_cancel.booth_block_daisy_troop_owner)):
                message_response = {
                    "message": "You cannot cancel a reservation for another troop",
                    "is_success": False,
                }
                message_response = json.dumps(message_response)
                return HttpResponse(message_response)
        else:
            # The user does not have the permissions to reserve a block
            # This should never occur, but adding this in the case something horribly goes wrong.
            message_response = {
                "message": "An unknown error occurred",
                "is_success": False,
            }
            message_response = json.dumps(message_response)
            return HttpResponse(message_response)

        if not daisy and block_to_cancel.cancel_block():
            # Successfully reserved the booth
            message_response = {
                "message": "Successfully cancelled reserved booth",
                "is_success": True,
            }
        elif daisy and block_to_cancel.cancel_daisy_reservation():
            # Successfully reserved the booth
            message_response = {
                "message": "Successfully cancelled reserved booth",
                "is_success": True,
            }
        else:
            message_response = {
                "message": "Failed to cancel reserved booth",
                "is_success": False,
            }
    else:
        message_response = {
            "message": "An unknown error occurred",
            "is_success": False,
        }
    message_response = json.dumps(message_response)
    return HttpResponse(message_response)

@login_required
def hold_block_for_cookie_captain(request, block_id):
    # Only admins have the ability to do this
    if request.user.has_perm("cookie_booths.block_reservation_admin"):
        block_to_hold = BoothBlock.objects.get(id=block_id)

        # A few things to validate in regards to the booth itself:
        # 1. It should not have an existing reservation on it
        # 2. It should not already be held by another cookie captain
        if (
            not block_to_hold.booth_block_held_for_cookie_captains
            and not block_to_hold.booth_block_reserved
        ):

            block_to_hold.hold_for_cookie_captains()
            message_response = {
                "message": "Successfully held booth for cookie captains",
                "is_success": True,
            }
        else:
            message_response = {
                "message": "Block is already reserved or being held for cookie captains",
                "is_success": False,
            }
    else:
        message_response = {
            "message": "You do not have permissions to hold booths",
            "is_success": False,
        }

    message_response = json.dumps(message_response)
    return HttpResponse(message_response)


@login_required
def cancel_hold_for_cookie_captain(request, block_id):
    # Only admins have the ability to do this
    if request.user.has_perm("cookie_booths.block_reservation_admin"):
        block_to_unhold = BoothBlock.objects.get(id=block_id)

        # We should validate that the booth is not currently being held
        if block_to_unhold.booth_block_held_for_cookie_captains:

            block_to_unhold.unhold_for_cookie_captains()
            message_response = {
                "message": "Successfully unheld booth for cookie captains",
                "is_success": True,
            }
        else:
            message_response = {
                "message": "Block is not currently held for cookie captains",
                "is_success": False,
            }
    else:
        message_response = {
            "message": "You do not have permissions to unhold booths",
            "is_success": False,
        }

    message_response = json.dumps(message_response)
    return HttpResponse(message_response)
