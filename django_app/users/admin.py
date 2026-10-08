from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserProfile, UserOTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("phone_number", "email", "user_type", "is_active", "is_verified", "created_at")
    list_filter = ("user_type", "is_active", "is_verified", "is_staff")
    search_fields = ("phone_number", "email")
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal", {"fields": ("email", "user_type")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "is_verified", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "password1", "password2", "user_type", "is_staff", "is_superuser"),
        }),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "gender", "created_at")
    search_fields = ("user__phone_number", "first_name", "last_name")


@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "is_used", "attempts", "expires_at", "created_at")
    list_filter = ("is_used",)
    search_fields = ("user__phone_number", "code")
    readonly_fields = ("created_at",)
