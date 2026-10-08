from rest_framework import generics, permissions
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    PhoneTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class PhoneTokenObtainPairView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer
    permission_classes = (permissions.AllowAny,)


class MeView(generics.RetrieveUpdateAPIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer
