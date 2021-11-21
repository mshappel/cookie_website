from django.urls import path
from . import views


app_name = 'cookie_booths'
urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    # Booths Home
    path('booths/', views.booth_locations, name='booth_locations'),
    # Create New Booth
    path('new_booth_location/', views.new_location, name='new_location'),
    # Create Booth Hours
    path('new_booth_hours/', views.new_location_hours, name='new_booth_hours'),
    # Edit Booth Page
    path('edit_booth/<int:booth_id>/', views.edit_location, name='edit_location'),
    # Edit Booth Hours
    path('edit_booth_hours/<int:booth_id>/', views.edit_location_hours, name='edit_booth_hours'),
    # Delete Booth
    path('booth_confirm_delete/<int:pk>', views.BoothLocationDelete.as_view(), name='delete_booth')
]
