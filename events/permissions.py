from rest_framework import permissions


class IsOrganizer(permissions.BasePermission):
    """Only users with role=organizer may pass (used on create endpoints)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_organizer)


class IsEventOwner(permissions.BasePermission):
    """Only the organizer who owns the event may edit/manage it."""

    def has_object_permission(self, request, view, obj):
        event = obj if hasattr(obj, "organizer") else obj.event
        return event.organizer_id == request.user.id


class IsStageEventOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.event.organizer_id == request.user.id
