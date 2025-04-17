"""Модуль с кастомными разрешениями для доступа к объектам."""

from rest_framework import permissions


class IsAuthorAdminOrReadOnly(permissions.BasePermission):
    """Разрешение для автора, администратора или только чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
