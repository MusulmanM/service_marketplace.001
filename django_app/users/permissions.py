from rest_framework import permissions

from .models import UserType


class IsClientRole(permissions.BasePermission):
    message = "Only clients can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.user_type == UserType.CLIENT
        )


class IsMasterRole(permissions.BasePermission):
    message = "Only masters can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.user_type == UserType.MASTER
        )


class IsAdminRole(permissions.BasePermission):
    message = "Only admins can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.user_type == UserType.ADMIN)
        )
