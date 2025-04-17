"""Вьюсеты для API-приложения."""

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from urlshort.models import ShortLink

from .filters import IngredientFilterSet, RecipeFilterSet
from .paginations import Pagination
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (AvatarSerializer, FavoriteRecipeSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, TagSerializer,
                          UrlshortSerializer)


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


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilterSet
    permission_classes = [AllowAny]
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet
    permission_classes = [IsAuthorAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        elif self.action == 'get_link':
            return UrlshortSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=[AllowAny],
        url_path='get-link',
        url_name='get-link',
    )
    def get_link(self, request, pk=None):
        """Генерация короткой ссылки на рецепт."""

        self.get_object()
        original_url = request.META.get('HTTP_REFERER')
        if original_url is None:
            url = reverse('api:recipe-detail', kwargs={'pk': pk})
            original_url = request.build_absolute_uri(url)
        serializer = self.get_serializer(
            data={'original_url': original_url},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        """Добавление/удаление рецепта в корзину покупок."""

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
                return Response(
                    {
                        'detail': f'Рецепт "{recipe.name}" уже добавлен '
                        'в список покупок.'
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ShoppingCart.objects.create(recipe=recipe, user=user)
            serializer = FavoriteRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            cart_item = ShoppingCart.objects.filter(recipe__id=pk, user=user)
            if cart_item.exists():
                cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {
                    'detail': f'Рецепт "{recipe.name}" отсутствует '
                    'в списке покупок.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def ingredients_to_txt(ingredients):
        """Формирование текста с ингредиентами."""

        return '\n'.join(
            f'{ingredient["ingredient__name"]} - {ingredient["sum"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            for ingredient in ingredients
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок в текстовом формате."""

        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shoppingcarts__user=request.user
            )
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(sum=Sum('amount'))
        )
        shopping_list = self.ingredients_to_txt(ingredients)
        return HttpResponse(shopping_list, content_type='text/plain')

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk):
        """Добавление/удаление рецепта в избранное."""

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(recipe=recipe,
                                             user=user).exists():
                return Response(
                    {
                        'detail': f'Рецепт "{recipe.name}" уже добавлен '
                        'в избранное.'
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            FavoriteRecipe.objects.create(recipe=recipe, user=user)
            serializer = FavoriteRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            favorite_entry = FavoriteRecipe.objects.filter(
                recipe=recipe, user=user
            )
            if favorite_entry.exists():
                favorite_entry.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {
                    'detail': f'Рецепт "{recipe.name}" не найден в избранном.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


@require_GET
def short_url(request, url_hash: str) -> HttpResponse:
    """Перенаправление по короткой ссылке."""

    original_url = get_object_or_404(ShortLink, url_hash=url_hash).original_url
    return redirect(original_url)
