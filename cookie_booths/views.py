import json
from datetime import datetime

from django.shortcuts import render, redirect
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin

# noinspection PyUnresolvedReferences
from users.models import User, Troop
from .forms import BoothLocationForm, BoothHoursForm
from .models import BoothLocation, BoothDay, BoothHours, BoothBlock, GIRL_SCOUT_TROOP_LEVELS_WITH_NONE


def index(request):
    """The home page for Cookie Booths"""
    return render(request, 'cookie_booths/index.html')


# -----------------------------------------------------------------------
# Booth Admin Functions
# -----------------------------------------------------------------------


@login_required
def booth_editor(request):
    """Display all booths for admins to edit"""
    booths = BoothLocation.objects.order_by('booth_location')
    context = {'booths': booths}
    return render(request, 'cookie_booths/booths.html', context)


@login_required
@permission_required('cookie_booths.booth_loc_creation', raise_exception=True)
def create_new_booth_location(request):
    """Create a new booth location"""
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = BoothLocationForm()
    else:
        # POST data submitted; process data.
        form = BoothLocationForm(data=request.POST)
        if form.is_valid():
            loc = form.save()
            return redirect('cookie_booths:edit_booth_hours', booth_id=loc.id)

    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'cookie_booths/new_booth_location.html', context)


@login_required
@permission_required('cookie_booths.booth_loc_updates', raise_exception=True)
def edit_booth_location(request, booth_id):
    """Edit an existing booth location"""
    booth = BoothLocation.objects.get(id=booth_id)

    if request.method != 'POST':
        # Initial request; pre-fill with the current entry.
        form = BoothLocationForm(instance=booth, booth_id=booth_id)
    else:
        # POST data submitted; process data.
        form = BoothLocationForm(instance=booth, data=request.POST, booth_id=booth_id)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('cookie_booths:booth_locations'))

    context = {'booth': booth, 'form': form}
    return render(request, 'cookie_booths/edit_booth.html', context)


@login_required
@permission_required('cookie_booths.booth_loc_updates', raise_exception=True)
def edit_booth_location_hours(request, booth_id):
    """Edit an existing booth location"""
    booth = BoothLocation.objects.get(id=booth_id)
    hours = BoothHours.objects.get(booth_location=booth.id)

    if request.method != 'POST':
        # Initial request; pre-fill with the current entry.
        form = BoothHoursForm(instance=hours)
    else:
        # POST data submitted; process data.
        form = BoothHoursForm(instance=hours, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('cookie_booths:booth_locations'))

    context = {'booth': booth, 'form': form}
    return render(request, 'cookie_booths/edit_booth_hours.html', context)


class BoothLocationDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    """Delete an existing booth location"""
    permission_required = 'cookie_booths.booth_loc_deletes'
    model = BoothLocation
    template_name = 'cookie_booths/booth_confirm_delete.html'
    success_url = reverse_lazy('cookie_booths:booth_locations')


@login_required
@permission_required('cookie_booths.enable_day', raise_exception=True)
def enable_location_by_block(request):
    booth_information = []
    booth_blocks_ = BoothBlock.objects.order_by('booth_day__booth', 'booth_day', 'booth_block_start_time')

    for booth in booth_blocks_:
        current_booth_information = {'booth_block_information': booth,
                                     'booth_owned_by_current_user': None}
        booth_information.append(current_booth_information)

    context = {'booth_blocks': booth_information,
               'available_troops': None,
               'page_title': "Enable Booths by Block",
               'reserve_or_enable_booths': "enable"}

    return render(request, 'cookie_booths/booth_blocks.html', context)


@login_required
def ajax_enable_location_by_block(request, block_id):
    is_success = False
    if request.method == 'POST':
        block_to_enable = BoothBlock.objects.get(id=block_id)
        if request.user.has_perm('cookie_booths.enable_day'):
            is_success = block_to_enable.enable_block()

    return HttpResponse(is_success)


@login_required
def ajax_disable_location_by_block(request, block_id):
    is_success = False
    if request.method == 'POST':
        block_to_enable = BoothBlock.objects.get(id=block_id)
        if request.user.has_perm('cookie_booths.enable_day'):
            is_success = block_to_enable.disable_block()

    return HttpResponse(is_success)


@login_required
@permission_required('cookie_booths.enable_day', raise_exception=True)
def enable_or_disable_day(request):
    booth_days = BoothDay.objects.order_by('booth', 'booth_day_date')

    context = {'booth_days': booth_days,
               'page_title': "Enable/Disable Booth Days",
               }

    return render(request, 'cookie_booths/enable_blocks.html', context)


@login_required
def enable_location_by_day(request):
    # Enable all dates for a particular booth up to and including a particular date
    if request.method == 'POST':
        booth_id = request.POST['booth_id']
        booth_day = BoothDay.objects.get(id=booth_id)
        if request.user.has_perm('cookie_booths.enable_day'):
            booth_day.enable_day()

    return HttpResponse()


@login_required
def disable_location_by_day(request):
    # Disable all dates for a particular booth up to and including a particular date
    if request.method == 'POST':
        booth_id = request.POST['booth_id']
        booth_day = BoothDay.objects.get(id=booth_id)
        if request.user.has_perm('cookie_booths.enable_day'):
            booth_day.disable_day()

    return HttpResponse()


@login_required
def enable_location_ffa(request, booth_id, date):
    # Enable free-for-all for a particular booth up to and including a particular date.
    # Will also enable dates up until that day if not already
    for booth_day in BoothDay.objects.filter(booth_id=booth_id, booth_day_date__lte=date):
        booth_day.enable_freeforall()

    return


@login_required
def enable_all_locations_ffa(request, date):
    # Enable free-for-all for all locations up to and including a particular date.
    # Will also enable those dates if not already
    for booth_day in BoothDay.objects.filter(booth_day_date__lte=date):
        booth_day.enable_freeforall()

    return


# -----------------------------------------------------------------------
# Booth User Functions
# -----------------------------------------------------------------------


@login_required
def booth_blocks(request):
    """Display all booths"""
    booth_blocks_ = BoothBlock.objects.order_by('booth_day__booth', 'booth_day', 'booth_block_start_time')
    booth_blocks_ = booth_blocks_.exclude(booth_block_enabled=False)
    available_troops = Troop.objects.order_by('troop_number')
    username = request.user.username
    booth_information = []

    try:
        user_troop = Troop.objects.get(troop_cookie_coordinator=username)

    except Troop.DoesNotExist:
        user_troop = None

    for booth in booth_blocks_:
        if user_troop is None:
            booth_owned_by_current_user_ = False
        else:
            if booth.booth_block_current_troop_owner == user_troop.troop_number:
                booth_owned_by_current_user_ = True
            else:
                booth_owned_by_current_user_ = False
        current_booth_information = {'booth_block_information': booth,
                                     'booth_owned_by_current_user': booth_owned_by_current_user_}
        booth_information.append(current_booth_information)

    context = {'booth_blocks': booth_information,
               'available_troops': available_troops,
               'page_title': "Make Booth Reservations",
               'reserve_or_enable_booths': "reserve"}
    return render(request, 'cookie_booths/booth_blocks.html', context)


@login_required
def booth_reservations(request):
    """Display all blocks currently reserved by the current user"""
    booth_blocks_ = BoothBlock.objects.order_by('booth_day__booth', 'booth_day', 'booth_block_start_time')
    booth_blocks_ = booth_blocks_.exclude(booth_block_enabled=False)
    available_troops = Troop.objects.order_by('troop_number')
    username = request.user.username
    booth_information = []

    try:
        user_troop = Troop.objects.get(troop_cookie_coordinator=username)
        booth_blocks_ = booth_blocks_.filter(booth_block_current_troop_owner=user_troop.troop_number)

    except Troop.DoesNotExist:
        user_troop = None

    for booth in booth_blocks_:
        if user_troop is None:
            booth_owned_by_current_user_ = False
        else:
            if booth.booth_block_current_troop_owner == user_troop.troop_number:
                booth_owned_by_current_user_ = True
            else:
                booth_owned_by_current_user_ = False
        current_booth_information = {'booth_block_information': booth,
                                     'booth_owned_by_current_user': booth_owned_by_current_user_}
        booth_information.append(current_booth_information)

    context = {'booth_blocks': booth_information,
               'available_troops': available_troops,
               'page_title': "Manage Your Booth Reservations",
               'reserve_or_enable_booths': "reserve"}
    return render(request, 'cookie_booths/booth_blocks.html', context)


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


@login_required
def reserve_block(request, block_id):
    # Attempt to reserve a block, based on the amount of tickets available to the user, FFA status, etc
    username = request.user.username
    message_response = {}

    if request.method == 'POST':
        block_to_reserve = BoothBlock.objects.get(id=block_id)
        if request.user.has_perm('cookie_booths.reserve_block_admin'):
            # The user is a SUCM or higher; we require a troop # from them for reservation
            troop_trying_to_reserve = request.POST['troop_number']
            if troop_trying_to_reserve == '':
                message_response = {
                    'message': "Please select a troop",
                    'is_success': False,
                }
                message_response = json.dumps(message_response)
                return HttpResponse(message_response)

            troop_trying_to_reserve_level = Troop.objects.get(troop_number=troop_trying_to_reserve).troop_level
            rem_tickets, rem_golden_tickets = Troop.objects.get(
                troop_number=troop_trying_to_reserve).get_num_tickets_remaining(
                block_to_reserve.booth_day.booth_day_date)

        elif request.user.has_perm('cookie_booths.reserve_block'):
            # The user is a TCC; the user's troop # is used for reservation
            troop_trying_to_reserve = Troop.objects.get(troop_cookie_coordinator=username).troop_number
            troop_trying_to_reserve_level = Troop.objects.get(troop_cookie_coordinator=username).troop_level
            rem_tickets, rem_golden_tickets = Troop.objects.get(
                troop_cookie_coordinator=username).get_num_tickets_remaining(
                block_to_reserve.booth_day.booth_day_date)
        else:
            # The user does not have the permissions to reserve a block
            # This should never occur, but adding this in the case something horribly goes wrong.
            return

        # Check if the troop has remaining tickets for the week
        tickets_remain = True
        if rem_tickets == 0:
            message_response = {
                'message': "No remaining tickets for this week",
                'is_success': False,
            }
            tickets_remain = False

        # Tickets may remain, but check to see if they may have a golden booth.
        if block_to_reserve.booth_day.booth_day_is_golden and rem_golden_tickets == 0:
            message_response = {
                'message': "No remaining golden tickets for this week",
                'is_success': False,
            }
            tickets_remain = False

        if not tickets_remain:
            # We have no more remaining tickets, alert the user.
            message_response = json.dumps(message_response)
            return HttpResponse(message_response)

        # Check if the troop is a valid troop level
        booth_restrictions_start = block_to_reserve.booth_day.booth.booth_block_level_restrictions_start
        booth_restrictions_end = block_to_reserve.booth_day.booth.booth_block_level_restrictions_end

        if booth_restrictions_start == 0:
            level_in_range = True
        else:
            level_in_range = troop_trying_to_reserve_level in range(booth_restrictions_start, booth_restrictions_end)

        if level_in_range:
            if block_to_reserve.reserve_block(troop_id=troop_trying_to_reserve):
                # Successfully reserved the booth
                message_response = {
                    'message': "Successfully reserved booth",
                    'is_success': True,
                }
            else:
                message_response = {
                    'message': "Failed to reserve booth",
                    'is_success': False,
                }
        else:
            message_response = {
                'message': "Booth has troop level restriction",
                'is_success': False,
            }
    else:
        message_response = {
            'message': "An unknown error occurred",
            'is_success': False,
        }
    message_response = json.dumps(message_response)
    return HttpResponse(message_response)


@login_required
def cancel_block(request, block_id):
    username = request.user.username

    if request.method == 'POST':
        block_to_cancel = BoothBlock.objects.get(id=block_id)
        if request.user.has_perm('cookie_booths.cancel_block_admin'):
            # The user is a SUCM or higher they can do this unconditionally
            pass
        elif request.user.has_perm('cookie_booths.cancel_block'):
            # The user is a TCC; the user's troop # is used to check if they can cancel
            troop_trying_to_cancel = Troop.objects.get(troop_cookie_coordinator=username).troop_number
            if troop_trying_to_cancel != block_to_cancel.booth_block_current_troop_owner:
                message_response = {
                    'message': "You cannot cancel a reservation for another troop",
                    'is_success': False,
                }
                message_response = json.dumps(message_response)
                return HttpResponse(message_response)
        else:
            # The user does not have the permissions to reserve a block
            # This should never occur, but adding this in the case something horribly goes wrong.
            message_response = {
                'message': "An unknown error occurred",
                'is_success': False,
            }
            message_response = json.dumps(message_response)
            return HttpResponse(message_response)

        if block_to_cancel.cancel_block():
            # Successfully reserved the booth
            message_response = {
                'message': "Successfully cancelled reserved booth",
                'is_success': True,
            }
        else:
            message_response = {
                'message': "Failed to cancel reserved booth",
                'is_success': False,
            }
    else:
        message_response = {
            'message': "An unknown error occurred",
            'is_success': False,
        }
    message_response = json.dumps(message_response)
    return HttpResponse(message_response)
