from django.urls import path
from . import views


app_name = 'cookie_booths'
urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    # Booths Home
    path('booths/edit_booth/', views.booth_editor, name='booth_locations'),
    # Create New Booth
    path('booths/new_booth_location/', views.create_new_booth_location, name='new_location'),
    # Edit Booth Page
    path('booths/edit_booth/<int:booth_id>/', views.edit_booth_location, name='edit_location'),
    # Edit Booth Hours
    path('booths/edit_booth/<int:booth_id>/hours/', views.edit_booth_location_hours, name='edit_booth_hours'),
    # Delete Booth
    path('booths/booth_confirm_delete/<int:pk>/', views.BoothLocationDelete.as_view(), name='delete_booth'),
    # Manage Booth Blocks Home
    path('booths/blocks/', views.booth_blocks, name='booth_blocks'),
    # Your Booth Reservations
    path('booths/blocks/reservations/', views.booth_reservations, name='booth_reservations'),
    # Make Booth Reservation
    path('booths/blocks/reservations/<int:block_id>', views.reserve_block, name='block_reservation'),
    # Cancel Booth Reservation
    path('booths/blocks/reservations/cancel/<int:block_id>', views.cancel_block, name='block_cancellation'),
    # User Enable Booth by Block
    path('booths/blocks/enable_blocks', views.enable_location_by_block, name='enable_location_by_block'),
    # AJAX Enable Booth by Block
    path('booths/blocks/enable_blocks/<int:block_id>', views.ajax_enable_location_by_block,
         name='ajax_enable_location_by_block'),
    # AJAX Disable Booth by Block
    path('booths/blocks/disable_blocks/<int:block_id>', views.ajax_disable_location_by_block,
         name='ajax_disable_location_by_block'),
    # User Enable Booth Day
    path('booths/blocks/enable_booth_days', views.enable_or_disable_day, name="enable_day"),
    # AJAX Enable Booth by Day
    path('booths/blocks/enable_booth_days/enable', views.enable_location_by_day, name="ajax_enable_day"),
    # AJAX Disable Booth by Day
    path('booths/blocks/enable_booth_days/disable', views.disable_location_by_day, name="ajax_disable_day"),
    #
    path('booths/enable_ffa', views.enable_all_locations_ffa, name="enable_ffa")
]
