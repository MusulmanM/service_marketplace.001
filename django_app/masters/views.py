import uuid

from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from users.permissions import IsMasterRole

from .models import MasterProfile, MasterService, ServiceCategory, ServiceCity
from .permissions import IsMasterProfileOwner, IsMasterServiceOwner
from .serializers import (
    MasterProfileSerializer,
    MasterServiceSerializer,
    ServiceCategorySerializer,
    ServiceCitySerializer,
)


def parse_bool(value):
    if value is None:
        return None
    value = value.lower()
    if value in ("1", "true", "yes", "on"):
        return True
    if value in ("0", "false", "no", "off"):
        return False
    return None


def parse_uuid(value):
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError):
        return None


class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceCategory.objects.filter(is_active=True).order_by("name")
    serializer_class = ServiceCategorySerializer
    permission_classes = (permissions.AllowAny,)


class ServiceCityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceCity.objects.filter(is_active=True).order_by("name")
    serializer_class = ServiceCitySerializer
    permission_classes = (permissions.AllowAny,)


class MasterProfileViewSet(viewsets.ModelViewSet):
    serializer_class = MasterProfileSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_queryset(self):
        queryset = (
            MasterProfile.objects.select_related("user")
            .prefetch_related("categories", "cities")
            .all()
        )

        category = self.request.query_params.get("category")
        if category:
            category_uuid = parse_uuid(category)
            category_filter = (
                Q(categories__slug__iexact=category)
                | Q(categories__name__icontains=category)
                | Q(services__category__slug__iexact=category)
                | Q(services__category__name__icontains=category)
            )
            if category_uuid:
                category_filter |= Q(categories__id=category_uuid) | Q(services__category_id=category_uuid)
            queryset = queryset.filter(category_filter)

        city = self.request.query_params.get("city")
        if city:
            city_uuid = parse_uuid(city)
            city_filter = Q(cities__slug__iexact=city) | Q(cities__name__icontains=city) | Q(city__iexact=city)
            if city_uuid:
                city_filter |= Q(cities__id=city_uuid)
            queryset = queryset.filter(city_filter)

        verified = parse_bool(self.request.query_params.get("verified"))
        if verified is not None:
            queryset = queryset.filter(is_verified=verified)

        available = parse_bool(self.request.query_params.get("available"))
        if available is not None:
            queryset = queryset.filter(is_available=available)

        query = self.request.query_params.get("q")
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(title__icontains=query)
                | Q(description__icontains=query)
            )

        return queryset.distinct()

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsMasterRole(), IsMasterProfileOwner()]
        return [permissions.IsAuthenticated(), IsMasterRole()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["get", "post", "put", "patch"], url_path="me")
    def me(self, request):
        profile = getattr(request.user, "master_profile", None)

        if request.method == "GET":
            if profile is None:
                raise NotFound("Master profile was not created yet.")
            serializer = self.get_serializer(profile)
            return Response(serializer.data)

        partial = request.method == "PATCH"
        if profile is None:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "POST":
            return Response(
                {"detail": "Master profile already exists. Use PUT or PATCH to update it."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(profile, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MasterServiceViewSet(viewsets.ModelViewSet):
    serializer_class = MasterServiceSerializer

    def get_queryset(self):
        queryset = (
            MasterService.objects.select_related("master", "master__user", "category")
            .prefetch_related("master__categories", "master__cities")
            .all()
        )

        user = self.request.user
        if self.action in ("list", "retrieve"):
            if user.is_authenticated and getattr(user, "is_master", False):
                queryset = queryset.filter(Q(is_active=True) | Q(master__user=user))
            else:
                queryset = queryset.filter(is_active=True)
        elif user.is_authenticated and getattr(user, "is_master", False):
            queryset = queryset.filter(master__user=user)

        category = self.request.query_params.get("category")
        if category:
            category_uuid = parse_uuid(category)
            category_filter = Q(category__slug__iexact=category) | Q(category__name__icontains=category)
            if category_uuid:
                category_filter |= Q(category_id=category_uuid)
            queryset = queryset.filter(category_filter)

        master = self.request.query_params.get("master")
        if master:
            master_uuid = parse_uuid(master)
            if master_uuid:
                queryset = queryset.filter(master_id=master_uuid)

        return queryset.distinct()

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsMasterRole(), IsMasterServiceOwner()]
        return [permissions.IsAuthenticated(), IsMasterRole()]

    def perform_create(self, serializer):
        serializer.save()
