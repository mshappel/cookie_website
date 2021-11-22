from django.urls import path
from . import views


app_name = 'cookie_booths'
urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    # Booths Home
    path('booths/', views.booth_locations, name='booth_locations'),
    # Create New Booth
    path('booths/new_booth_location/', views.new_location, name='new_location'),
    # Edit Booth Page
    path('booths/edit_booth/<int:booth_id>/', views.edit_location, name='edit_location'),
    # Edit Booth Hours
    path('booths/edit_booth_hours/<int:booth_id>/', views.edit_location_hours, name='edit_booth_hours'),
    # Delete Booth
    path('booths/booth_confirm_delete/<int:pk>/', views.BoothLocationDelete.as_view(), name='delete_booth'),
    # Booth Blocks Home
    path('blocks/', views.booth_blocks, name='booth_blocks'),
    # Booth Reservations
    path('reservations/', views.booth_reservations, name='booth_reservations')
]
