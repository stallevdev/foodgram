"""Вьюсеты для API-приложения."""

from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .paginations import Pagination


class CustomUserViewSet(UserViewSet):
    """Вьюсет для управления пользователями."""

    pagination_class = Pagination

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_name='me',
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)
