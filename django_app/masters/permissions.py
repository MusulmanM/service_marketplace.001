from rest_framework import permissions


class IsMasterProfileOwner(permissions.BasePermission):
    message = "You can edit only your own master profile."

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated and obj.user_id == request.user.id)


class IsMasterServiceOwner(permissions.BasePermission):
    message = "You can edit only your own services."

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and request.user.is_authenticated
            and obj.master.user_id == request.user.id
        )
