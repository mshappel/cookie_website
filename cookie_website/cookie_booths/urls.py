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
]
