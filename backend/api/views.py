"""Вьюсеты для API-приложения."""

from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import Tag

from .paginations import Pagination
from .serializers import AvatarSerializer, TagSerializer


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

    @action(
        detail=False,
        methods=['GET', 'PUT', 'DELETE'],
        serializer_class=AvatarSerializer,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
        url_name='me-avatar',
    )
    def avatar(self, request):
        """Управление аватаром пользователя."""

        if request.method == 'GET':
            serializer = self.manage_avatar()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PUT':
            serializer = self.manage_avatar(request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            self.manage_avatar({'avatar': None})
            return Response(
                {"detail": "Аватар удалён."}, status=status.HTTP_204_NO_CONTENT
            )

    def manage_avatar(self, avatar_data=None):
        """Получение или изменение аватара."""

        user = self.request.user
        if avatar_data is None:
            serializer = AvatarSerializer(user)
        else:
            serializer = AvatarSerializer(user, data=avatar_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return serializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [AllowAny]
