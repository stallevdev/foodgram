# Generated by Django 4.2.20 on 2025-04-15 11:12

from django.db import migrations, models

import urlshort.models


class Migration(migrations.Migration):
    """Миграция для изменения структуры базы данных."""

    initial = True

    dependencies = []  # type: ignore

    operations = [
        migrations.CreateModel(
            name="ShortLink",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "original_url",
                    models.CharField(
                        max_length=256, verbose_name="Оригинальная ссылка"
                    ),
                ),
                (
                    "url_hash",
                    models.CharField(
                        default=urlshort.models.generate_hash,
                        max_length=15,
                        unique=True,
                        verbose_name="Хэш ссылки",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ссылка",
                "verbose_name_plural": "Ссылки",
                "ordering": ["id"],
            },
        ),
    ]
