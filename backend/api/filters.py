"""Наборы фильтров для моделей API."""

from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet

from recipes.models import Ingredient


class IngredientFilterSet(FilterSet):
    """Фильтр для ингредиентов."""

    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        """Мета."""

        model = Ingredient
        fields = ('name',)
