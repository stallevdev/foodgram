"""Конфигурация приложения Django."""

from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Конфигурация приложения 'Рецепты'."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    verbose_name = 'Рецепты'
