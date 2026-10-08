from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    MasterProfileViewSet,
    MasterServiceViewSet,
    ServiceCategoryViewSet,
    ServiceCityViewSet,
)

router = DefaultRouter()
router.register("categories", ServiceCategoryViewSet, basename="service-category")
router.register("cities", ServiceCityViewSet, basename="service-city")
router.register("services", MasterServiceViewSet, basename="master-service")
router.register("", MasterProfileViewSet, basename="master-profile")

urlpatterns = [
    path("", include(router.urls)),
]
