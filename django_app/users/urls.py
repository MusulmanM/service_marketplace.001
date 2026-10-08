from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import MeView, PhoneTokenObtainPairView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("token/", PhoneTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="user-me"),
]
