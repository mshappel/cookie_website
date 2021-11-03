from django.shortcuts import render


def index(request):
    """The home page for Cookie Booths"""
    return render(request, 'cookie_booths/index.html')


def new_location(request):
    # Create new BoothLocationForm
    return


def edit_location(request, booth_id):
    # Get existing Booth_ID, populate BoothLocationForm
    return


def edit_location_hours(request, booth_id):
    # Get existing hours if set, open form
    # Read form output, call model function to add/edit existing booth days
    return


def enable_location(request, booth_id, date):
    # Enable all dates for a particular boot up to and including a particular date
    return


def enable_all_locations(request, date):
    # Enable all dates for all locations up to and including a particular date
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
