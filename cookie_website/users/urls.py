"""Defines URL patterns for users"""

from django.urls import path, include

from . import views


app_name = 'users'
urlpatterns = [
    # Include default auth urls.
    path('', include('django.contrib.auth.urls')),
    # Registration page.
    path('register/', views.register, name='register'),
    # Troops Home
    path('troop/', views.troops, name='troops'),
    # Create New Troop
    path('troop/new_troop', views.create_troop, name='create_troop'),
    # Edit Troop Page
    path('troop/edit_troop/<int:troop_number>/', views.edit_troop, name='edit_troop'),
    # Delete Troop
    path('troop/troop_confirm_delete/<int:pk>/', views.TroopDelete.as_view(), name='delete_troop'),
]