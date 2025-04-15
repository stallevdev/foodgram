"""Сериализаторы для API-приложения."""

import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from users.models import Subscriber, User


class Base64ImageField(serializers.ImageField):
    """Поле для обработки изображений в Base64 формате."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            img_format, imgstr = data.split(';base64,')
            ext = img_format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserCreateSerializer):
    """Кастомный сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(allow_null=True, label='Аватар')

    class Meta:
        """Мета."""

        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователя."""

        user = self.context.get('request')
        return bool(
            user
            and user.user.is_authenticated
            and Subscriber.objects.filter(author=obj, user=user.user).exists()
        )


class CustomUserCreateSerializer(CustomUserSerializer):
    """Сериализатор для создания пользователя."""

    password = serializers.CharField(write_only=True, label='Пароль')

    class Meta:
        """Мета."""

        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара пользователя."""

    avatar = Base64ImageField(allow_null=True, label='Аватар')

    class Meta:
        """Мета."""

        model = User
        fields = ('avatar',)
