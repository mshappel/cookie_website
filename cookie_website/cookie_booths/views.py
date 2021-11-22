import json

from django.shortcuts import render, redirect
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from .forms import BoothLocationForm, BoothHoursForm
from .models import BoothLocation, BoothDay, BoothHours


def index(request):
    """The home page for Cookie Booths"""
    return render(request, 'cookie_booths/index.html')


def booth_locations(request):
    """Display all booths"""
    booths = BoothLocation.objects.order_by('booth_location')
    context = {'booths': booths}
    return render(request, 'cookie_booths/booths.html', context)


def new_location(request):
    """Add a new booth location"""
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = BoothLocationForm()
    else:
        # POST data submitted; process data.
        form = BoothLocationForm(data=request.POST)
        if form.is_valid():
            loc = form.save()
            print(loc.id)
            return redirect('cookie_booths:edit_booth_hours', booth_id=loc.id)

    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'cookie_booths/new_booth_location.html', context)


def edit_location(request, booth_id):
    """Edit an existing booth location"""
    booth = BoothLocation.objects.get(id=booth_id)

    if request.method != 'POST':
        # Initial request; pre-fill with the current entry.
        form = BoothLocationForm(instance=booth)
    else:
        # POST data submitted; process data.
        form = BoothLocationForm(instance=booth, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('cookie_booths:booth_locations'))

    context = {'booth': booth, 'form': form}
    return render(request, 'cookie_booths/edit_booth.html', context)


class BoothLocationDelete(DeleteView):
    model = BoothLocation
    template_name = 'cookie_booths/booth_confirm_delete.html'
    success_url = reverse_lazy('cookie_booths:booth_locations')


def edit_location_hours(request, booth_id):
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
            # TODO: We need to have dates. Does does not validate if a date exists.
            form.save()
            return HttpResponseRedirect(reverse_lazy('cookie_booths:booth_locations'))

    context = {'booth': booth, 'form': form}
    return render(request, 'cookie_booths/edit_booth_hours.html', context)


def enable_location(request, booth_id, date):
    # Enable all dates for a particular booth up to and including a particular date
    for booth_day in BoothDay.objects.filter(booth_id=booth_id, booth_day_date__lte=date):
        booth_day.enable_day()

    return


def enable_all_locations(request, date):
    # Enable all dates for all locations up to and including a particular date
    for booth_day in BoothDay.objects.filter(booth_day_date__lte=date):
        booth_day.enable_day()

    return


def enable_location_ffa(request, booth_id, date):
    # Enable free-for-all for a particular booth up to and including a particular date.
    # Will also enable dates up until that day if not already
    for booth_day in BoothDay.objects.filter(booth_id=booth_id, booth_day_date__lte=date):
        booth_day.enable_freeforall()

    return


def enable_all_locations_ffa(request, date):
    # Enable free-for-all for all locations up to and including a particular date.
    # Will also enable those dates if not already
    for booth_day in BoothDay.objects.filter(booth_day_date__lte=date):
        booth_day.enable_freeforall()

    return


def disable_all_locations(request, date):
    # Disable all locations, including any active FFA, up to and including a particular date
    for booth_day in BoothDay.objects.filter(booth_day_date__lte=date):
        booth_day.disable_freeforall()

    return


def get_available_dates(request):
    # Go through all booth locations, and based on an intersection of those, figure out the list of available
    # Dates for selecting blocks
    return


def get_available_blocks(request, date):
    # Go through all booth locations open on a particular date, and return all of the blocks,
    # Probably ordered and grouped by location in some kind of (location/location_name, [block list]) tuple format
    return


def is_block_enabled(request, block_id):
    # Check if block is enabled for reservation. May still be cancelable
    return


def is_block_reserved(request, block_id):
    # Check if block is reserved by a user that is *not* the current user
    return


def is_block_reserved_by_user(request, block_id):
    # Check if block is reserved by the current user, and thus can be cancelled
    return


def reserve_block(request, block_id):
    # Attempt to reserve a block, based on the amount of tickets available to the user, FFA status, etc
    # Some kind of error if it fails?
    return


def cancel_block(request, block_id):
    # Attempt to cancel a block, considering it belongs to the current user
    return
