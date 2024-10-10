"""Административный интерфейс для моделей пользователей и подписок."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import Subscriber, User


class SubscriberInline(admin.TabularInline):
    """Подписчики пользователя."""

    model = Subscriber
    fk_name = 'author'
    extra = 1


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для пользователей."""

    @admin.display(description='Подписчики')
    def get_subscribers(self, obj):
        """Отображение подписчиков в списке пользователей."""
        subscribers = Subscriber.objects.filter(author_id=obj.id)
        return [sub.user for sub in subscribers]

    inlines = [SubscriberInline]
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'get_subscribers',
    )
    list_display_links = ('username',)
    list_filter = ('username',)
    search_fields = ('username',)
    search_help_text = 'Уникальный юзернейм для поиска.'
    ordering = ['id']


admin.site.unregister(Group)
