"""Модуль настройки админки для модели коротких ссылок."""

from django.contrib import admin

from .models import ShortLink


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    """Админка для коротких ссылок."""

    list_display = ('id', 'original_url', 'url_hash')
    list_display_links = ('original_url',)
