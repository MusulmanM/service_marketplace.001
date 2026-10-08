from django.contrib import admin

from .models import (
    Order,
    OrderPhoto,
    OrderReport,
    OrderReview,
    OrderStatusHistory,
)


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ("created_at",)


class OrderPhotoInline(admin.TabularInline):
    model = OrderPhoto
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "master", "title", "status", "price", "scheduled_at", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "client__phone_number", "master__user__phone_number", "master__name")
    inlines = [OrderPhotoInline, OrderStatusHistoryInline]
    readonly_fields = ("created_at", "updated_at", "completed_at")


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "old_status", "new_status", "changed_by", "created_at")
    list_filter = ("new_status",)
    search_fields = ("order__id", "changed_by__phone_number")
    readonly_fields = ("created_at",)


@admin.register(OrderPhoto)
class OrderPhotoAdmin(admin.ModelAdmin):
    list_display = ("order", "photo_type", "uploaded_by", "created_at")
    list_filter = ("photo_type",)
    search_fields = ("order__id", "uploaded_by__phone_number")
    readonly_fields = ("created_at",)


@admin.register(OrderReport)
class OrderReportAdmin(admin.ModelAdmin):
    list_display = ("order", "master", "created_at", "updated_at")
    search_fields = ("order__id", "master__name", "master__user__phone_number", "text")
    readonly_fields = ("created_at", "updated_at")


@admin.register(OrderReview)
class OrderReviewAdmin(admin.ModelAdmin):
    list_display = ("order", "client", "master", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("order__id", "client__phone_number", "master__name")
    readonly_fields = ("created_at", "updated_at")
