"""
Административная настройка моделей рецептов, ингредиентов,
тегов и корзины.
"""

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для тегов."""

    list_display = ('id', 'name', 'slug')
    list_display_links = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """Админка для ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)
    search_help_text = 'Уникальное название для поиска.'


class RecipeTagInline(admin.TabularInline):
    """Инлайн для тегов рецепта."""

    model = RecipeTag
    extra = 1


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн для ингредиентов рецепта."""

    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецептов."""

    @admin.display(description='Теги')
    def get_tags(self, obj):
        """Список тегов рецепта."""
        return ', '.join([tag.name for tag in obj.tags.all()])

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        """Список ингредиентов рецепта."""
        return ', '.join(
            [
                f'{ingredients.ingredient} - {ingredients.amount} '
                f'{ingredients.ingredient.measurement_unit}'
                for ingredients in obj.ingredient_list.all()
            ]
        )

    inlines = [RecipeTagInline, RecipeIngredientInline]
    list_display = ('id', 'name', 'author', 'get_tags', 'get_ingredients')
    list_display_links = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)
    search_help_text = 'Название для поиска.'


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    """Админка для избранных рецептов."""

    list_display = ('id', 'recipe', 'user')
    list_display_links = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для корзины покупок."""

    list_display = ('id', 'recipe', 'user')
    list_display_links = ('user',)
