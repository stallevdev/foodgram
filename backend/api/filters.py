"""Наборы фильтров для моделей API."""

from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilterSet(FilterSet):
    """Фильтр для ингредиентов."""

    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        """Мета."""

        model = Ingredient
        fields = ('name',)


class RecipeFilterSet(FilterSet):
    """Фильтр для рецептов."""

    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр по избранным рецептам."""

        user = (
            self.request.user
            if self.request.user.is_authenticated
            else None
        )
        if value and user:
            return queryset.filter(favoriterecipes__user_id=user.id)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр по рецептам в корзине."""

        user = (
            self.request.user
            if self.request.user.is_authenticated
            else None
        )
        if value and user:
            return queryset.filter(shoppingcarts__user_id=user.id)
        return queryset

    class Meta:
        """Мета."""

        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
