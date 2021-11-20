from django.urls import path
from . import views


app_name = 'cookie_booths'
urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    path('booths/', views.booth_locations, name='booth_locations'),
    path('new_booth_location/', views.new_location, name='new_location'),

    path('load_location/', views.load_location, name='load_location')
]
