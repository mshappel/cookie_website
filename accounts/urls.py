from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import SignUpView, UserPreferenceView

app_name = "accounts"

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("preferences/<int:pk>/", UserPreferenceView.as_view(), name="user_preference"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
