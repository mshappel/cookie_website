"""Defines URL patterns for users"""

from django.urls import path, include

from . import views


app_name = 'troops'
urlpatterns = [
    # Troops Home
    path('', views.TroopListView.as_view(), name='troops'),
    # Create New Troop
    path('new/', views.create_troop, name='create_troop'),
    # Edit Troop Page
    path('edit/<int:troop_number>/', views.edit_troop, name='edit_troop'),
    # Delete Troop
    path('confirm_delete/<int:pk>/', views.TroopDelete.as_view(), name='delete_troop'),
]
