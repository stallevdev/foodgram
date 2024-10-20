"""Сериализаторы для API-приложения."""

import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.reverse import reverse
from urlshort.models import ShortLink
from users.models import Subscriber, User

from foodgram.constants import PAGES_LIMIT_DEFAULT


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


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        """Мета."""

        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        """Мета."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        """Мета."""

        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""

    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = IngredientRecipeReadSerializer(
        source='ingredient_list', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Мета."""

        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def check_user_status(self, obj, model_class):
        """Проверка наличия рецепта в переданном классе модели."""

        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and model_class.objects.filter(
                recipe=obj, user=request.user).exists()
        )

    def get_is_favorited(self, obj):
        """Проверка, в избранном ли рецепт."""

        return self.check_user_status(obj, FavoriteRecipe)

    def get_is_in_shopping_cart(self, obj):
        """Проверка, в корзине ли рецепт."""

        return self.check_user_status(obj, ShoppingCart)


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов рецепта."""

    id = serializers.IntegerField()

    class Meta:
        """Мета."""

        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        label='Теги',
    )
    ingredients = IngredientRecipeWriteSerializer(
        many=True,
        label='Ингредиенты',
    )
    image = Base64ImageField(allow_null=True, label='Изображение')

    class Meta:
        """Мета."""

        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_tags(self, value):
        """Проверка валидности тегов."""

        if not value:
            raise serializers.ValidationError(
                'Поле "tags" не может быть пустым.'
            )

        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Теги должны быть уникальными.'
            )

        return value

    def validate_ingredients(self, value):
        """Проверка валидности ингредиентов."""

        if not value:
            raise serializers.ValidationError(
                'Поле "ingredients" не может быть пустым.'
            )
        ingredient_ids = [ingredient['id'] for ingredient in value]
        existing_ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        if len(existing_ingredients) != len(ingredient_ids):
            missing_ids = set(ingredient_ids) - set(
                existing_ingredients.values_list('id', flat=True)
            )
            raise serializers.ValidationError(
                f'Ингредиенты с id {missing_ids} не существуют.'
            )
        return value

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance, context={'request': self.context.get('request')}
        )
        return serializer.data

    def create_tags(self, tags, recipe):
        """Создание тегов рецепта."""

        recipe.tags.set(tags)

    def create_ingredients(self, ingredients, recipe):
        """Создание ингредиентов рецепта."""

        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['id']
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(
                ingredient=ingredient, recipe=recipe, amount=amount
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.get('tags')
        if tags is None:
            raise serializers.ValidationError(
                {'tags': 'Это поле обязательно для заполнения.'}
            )
        ingredients = validated_data.get('ingredients')
        if ingredients is None:
            raise serializers.ValidationError(
                {'ingredients': 'Это поле обязательно для заполнения.'}
            )
        RecipeTag.objects.filter(recipe=instance).delete()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)


class UrlshortSerializer(serializers.ModelSerializer):
    """Сериализатор для коротких ссылок."""

    class Meta:
        """Мета."""

        model = ShortLink
        fields = ('original_url',)

    def get_short_link(self, obj):
        """Генерация короткой ссылки."""

        request = self.context.get('request')
        return request.build_absolute_uri(reverse('api:short_url',
                                                  args=[obj.url_hash]))

    def create(self, validated_data):
        instance, _ = ShortLink.objects.get_or_create(**validated_data)
        return instance

    def to_representation(self, instance):
        return {'short-link': self.get_short_link(instance)}


class RecipeSummarySerializer(serializers.ModelSerializer):
    """Краткий сериализатор рецепта."""

    class Meta:
        """Мета."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriberDetailSerializer(serializers.ModelSerializer):
    """Сериализатор подписчика с детальной информацией."""

    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField(source='author.avatar')

    class Meta:
        """Мета."""

        model = Subscriber
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки на автора."""

        user = self.context.get('request').user
        return Subscriber.objects.filter(author=obj.author, user=user).exists()

    def get_recipes(self, obj):
        """Получение рецептов автора."""

        request = self.context.get('request')
        limit = request.GET.get('recipes_limit', PAGES_LIMIT_DEFAULT)
        try:
            limit = int(limit)
        except ValueError:
            pass
        return RecipeSummarySerializer(
            Recipe.objects.filter(author=obj.author)[:limit],
            many=True,
            context={'request': request},
        ).data

    def get_recipes_count(self, obj):
        """Количество рецептов у автора."""

        return Recipe.objects.filter(author=obj.author).count()


class SubscriberSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    class Meta:
        """Мета."""

        model = Subscriber
        fields = '__all__'

    def to_representation(self, instance):
        return SubscriberDetailSerializer(instance, context=self.context).data

    def validate_author(self, value):
        """Проверка подписки на себя."""

        if self.context['request'].user == value:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя.'
            )
        return value


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    image = Base64ImageField()

    class Meta:
        """Мета."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
