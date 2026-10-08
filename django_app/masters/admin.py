from django.contrib import admin

from .models import MasterProfile, MasterService, ServiceCategory, ServiceCity


@admin.register(MasterProfile)
class MasterProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "title",
        "rating",
        "reviews_count",
        "is_available",
        "is_verified",
        "experience_years",
    )
    list_filter = ("is_available", "is_verified", "categories", "cities")
    search_fields = ("user__phone_number", "name", "title", "city")
    filter_horizontal = ("categories", "cities")
    readonly_fields = ("rating", "reviews_count", "created_at", "updated_at")


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")


@admin.register(ServiceCity)
class ServiceCityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")


@admin.register(MasterService)
class MasterServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "master", "category", "price", "duration_minutes", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("title", "master__user__phone_number", "master__name")
