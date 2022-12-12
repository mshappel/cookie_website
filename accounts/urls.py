from django.urls import path
from .views import SignUpView, UserPreferenceView 

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("preferences/<int:pk>/", UserPreferenceView.as_view(), name='user_preference')
]
