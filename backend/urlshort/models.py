"""Модуль моделей и генерации коротких ссылок."""

import string
from random import choice, randint

from django.db import models

from foodgram.constants import (HASH_FIELD_LENGTH, MAX_HASH_LENGTH,
                                MAX_URL_LENGTH, MIN_HASH_LENGTH)


def generate_hash():
    """Генерирует случайную строку."""

    return ''.join(
        choice(string.ascii_letters + string.digits)
        for _ in range(randint(MIN_HASH_LENGTH, MAX_HASH_LENGTH))
    )


class ShortLink(models.Model):
    """Модель коротких ссылок"""

    original_url = models.CharField(
        max_length=MAX_URL_LENGTH,
        verbose_name='Оригинальная ссылка',
    )
    url_hash = models.CharField(
        unique=True,
        max_length=HASH_FIELD_LENGTH,
        default=generate_hash,
        verbose_name='Хэш ссылки',
    )

    class Meta:
        """Мета."""

        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'
        ordering = ['id']

    def __str__(self):
        return f'{self.original_url} → {self.url_hash}'
