from rest_framework import permissions

from users.models import UserType

from .models import Order


def get_order_from_object(obj):
    if isinstance(obj, Order):
        return obj
    return getattr(obj, "order", None)


def get_master_profile(user):
    return getattr(user, "master_profile", None)


def is_admin_user(user):
    return bool(user and user.is_authenticated and (user.is_staff or user.user_type == UserType.ADMIN))


class IsOrderParticipantOrAdmin(permissions.BasePermission):
    message = "You must be a participant of this order."

    def has_object_permission(self, request, view, obj):
        order = get_order_from_object(obj)
        if not order or not request.user or not request.user.is_authenticated:
            return False
        if is_admin_user(request.user):
            return True
        if order.client_id == request.user.id:
            return True
        master_profile = get_master_profile(request.user)
        return bool(master_profile and order.master_id == master_profile.id)


class IsAssignedMasterOrAdmin(permissions.BasePermission):
    message = "Only the assigned master can perform this action."

    def has_object_permission(self, request, view, obj):
        order = get_order_from_object(obj)
        if not order or not request.user or not request.user.is_authenticated:
            return False
        if is_admin_user(request.user):
            return True
        master_profile = get_master_profile(request.user)
        return bool(master_profile and order.master_id == master_profile.id)


class IsOrderClient(permissions.BasePermission):
    message = "Only the order client can perform this action."

    def has_object_permission(self, request, view, obj):
        order = get_order_from_object(obj)
        return bool(
            order
            and request.user
            and request.user.is_authenticated
            and order.client_id == request.user.id
        )
