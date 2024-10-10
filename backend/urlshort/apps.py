"""Конфигурация приложения Django."""

from django.apps import AppConfig


class UrlshortConfig(AppConfig):
    """Конфигурация приложения 'Короткий URL-адрес'."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'urlshort'
    verbose_name = 'Короткий URL-адрес'
