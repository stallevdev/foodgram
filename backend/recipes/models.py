"""
Модели для приложения рецептов: теги, ингредиенты, рецепты,
избранное и корзина.
"""

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from users.models import User

from foodgram.constants import (AMOUNT_MIN, COOKING_MIN_TIME,
                                INGREDIENT_MAX_LENGTH, RECIPE_MAX_LENGTH,
                                SLUG_REGEXVALIDATOR, TAG_MAX_LENGTH,
                                UNIT_INGREDIENT_MAX_LENGTH)


class Tag(models.Model):
    """Модель тег."""

    name = models.CharField(
        unique=True,
        max_length=TAG_MAX_LENGTH,
        verbose_name='Уникальное название',
    )
    slug = models.SlugField(
        unique=True,
        max_length=TAG_MAX_LENGTH,
        validators=[
            RegexValidator(
                SLUG_REGEXVALIDATOR,
                message=(
                    'Slug может содержать только буквы, '
                    'цифры, дефисы и нижние подчеркивания.'
                ),
            )
        ],
        verbose_name='Уникальный слаг',
    )

    class Meta:
        """Мета."""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['id']

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """Модель ингредиент."""

    name = models.CharField(
        unique=True,
        max_length=INGREDIENT_MAX_LENGTH,
        verbose_name='Уникальное название',
    )
    measurement_unit = models.CharField(
        max_length=UNIT_INGREDIENT_MAX_LENGTH,
        verbose_name='Единицы измерения',
    )

    class Meta:
        """Мета."""

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit',
            )
        ]
        ordering = ['id']

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """Модель рецепт."""

    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes',
        verbose_name='Список тегов',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Пользователь (В рецепте - автор рецепта)',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Список ингредиентов',
    )
    is_favorited = models.BooleanField(
        default=True,
        verbose_name='Находится ли в избранном',
    )
    is_in_shopping_cart = models.BooleanField(
        default=True,
        verbose_name='Находится ли в корзине',
    )
    name = models.CharField(
        max_length=RECIPE_MAX_LENGTH,
        verbose_name='Название',
    )
    image = models.ImageField(
        blank=True,
        null=True,
        verbose_name='Ссылка на картинку на сайте',
        upload_to='recipes/',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                COOKING_MIN_TIME,
                message='Минимальное время приготовления',
            )
        ],
        verbose_name='Время приготовления (в минутах)',
    )

    class Meta:
        """Мета."""

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['id']

    def __str__(self):
        return f'{self.name}'


class RecipeTag(models.Model):
    """Модель для связи рецептов и тегов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tag_list',
        verbose_name='Рецепт',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_recipe',
        verbose_name='Тег',
    )

    class Meta:
        """Мета."""

        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag',
            )
        ]

    def __str__(self):
        return f'{self.recipe} - {self.tag}'


class RecipeIngredient(models.Model):
    """Модель для связи рецептов и ингредиентов с указанием количества."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                AMOUNT_MIN,
                message='Минимальное количество',
            )
        ],
        verbose_name='Количество',
    )

    class Meta:
        """Мета."""

        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            )
        ]

    def __str__(self):
        return (
            f'{self.recipe}: {self.ingredient} - {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class FavoriteRecipe(models.Model):
    """Модель для хранения информации об избранных рецептах пользователя."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favoriterecipes',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoriterecipes',
        verbose_name='Пользователь',
    )

    class Meta:
        """Мета."""

        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite',
            )
        ]
        ordering = ['id']

    def __str__(self):
        return f'{self.recipe} - {self.user}'


class ShoppingCart(models.Model):
    """
    Модель для хранения рецептов, добавленных
    пользователем в корзину покупок.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcarts',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcarts',
        verbose_name='Пользователь',
    )

    class Meta:
        """Мета."""

        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shopping_cart',
            )
        ]
        ordering = ['id']

    def __str__(self):
        return f'{self.recipe} - {self.user}'
