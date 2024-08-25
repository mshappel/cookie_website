from django.urls import path

from cookie_booths.views import booth_administration, booth_users

app_name = "cookie_booths"


urlpatterns = [
    # User-related URLs
    path(
        "booth_blocks/",
        booth_users.booth_blocks,
        name="booth_blocks",
    ),
    path(
        "booth_reservations/",
        booth_users.booth_reservations,
        name="booth_reservations",
    ),
    path(
        "reserve_block/<str:daisy>/<int:block_id>/",
        booth_users.reserve_block,
        name="reserve_block",
    ),
    path(
        "cancel_block/<str:daisy>/<int:block_id>/",
        booth_users.cancel_block,
        name="cancel_block",
    ),
    path(
        "hold_block_for_cookie_captain/<int:block_id>/",
        booth_users.hold_block_for_cookie_captain,
        name="hold_block_for_cookie_captain",
    ),
    path(
        "cancel_hold_for_cookie_captain/<int:block_id>/",
        booth_users.cancel_hold_for_cookie_captain,
        name="cancel_hold_for_cookie_captain",
    ),
    # Admin-related URLs
    path(
        "booth_editor/",
        booth_administration.booth_editor,
        name="booth_editor",
    ),
    path(
        "create_new_booth_location/",
        booth_administration.create_new_booth_location,
        name="create_new_booth_location",
    ),
    path(
        "edit_booth_location/<int:booth_id>/",
        booth_administration.edit_booth_location,
        name="edit_booth_location",
    ),
    path(
        "edit_booth_location_hours/<int:booth_id>/",
        booth_administration.edit_booth_location_hours,
        name="edit_booth_location_hours",
    ),
    path(
        "delete_booth_location/<int:pk>/",
        booth_administration.BoothLocationDelete.as_view(),
        name="delete_booth_location",
    ),
    path(
        "enable_location_by_block/",
        booth_administration.enable_location_by_block,
        name="enable_location_by_block",
    ),
    path(
        "ajax_enable_location_by_block/<int:block_id>/",
        booth_administration.ajax_enable_location_by_block,
        name="ajax_enable_location_by_block",
    ),
    path(
        "ajax_disable_location_by_block/<int:block_id>/",
        booth_administration.ajax_disable_location_by_block,
        name="ajax_disable_location_by_block",
    ),
    path(
        "enable_or_disable_day/",
        booth_administration.enable_or_disable_day,
        name="enable_or_disable_day",
    ),
    path(
        "enable_location_by_day/",
        booth_administration.enable_location_by_day,
        name="enable_location_by_day",
    ),
    path(
        "disable_location_by_day/",
        booth_administration.disable_location_by_day,
        name="disable_location_by_day",
    ),
]
