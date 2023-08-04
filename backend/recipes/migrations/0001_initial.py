# Generated by Django 3.2 on 2023-08-03 01:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Ingredient",
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
                ("name", models.CharField(max_length=200)),
                ("measurement_unit", models.CharField(max_length=200)),
            ],
            options={
                "verbose_name": "игредиент",
                "verbose_name_plural": "ингредиенты",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Recipe",
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
                ("pub_date", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                (
                    "image",
                    models.ImageField(
                        default=None, null=True, upload_to="recipes/images/"
                    ),
                ),
                ("text", models.TextField()),
                ("cooking_time", models.PositiveIntegerField()),
            ],
            options={
                "verbose_name": "рецепт",
                "verbose_name_plural": "рецепты",
                "ordering": ("-pub_date",),
            },
        ),
        migrations.CreateModel(
            name="Tag",
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
                ("name", models.CharField(max_length=200)),
                ("color", models.CharField(max_length=7)),
                (
                    "slug",
                    models.SlugField(
                        max_length=200, unique=True, verbose_name="Slug-тега"
                    ),
                ),
            ],
            options={
                "verbose_name": "тег",
                "verbose_name_plural": "Теги",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="RecipeIngredient",
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
                ("amount", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "ingredient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="recipes.ingredient",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipe_ingredients",
                        to="recipes.recipe",
                    ),
                ),
            ],
            options={
                "ordering": ("recipe",),
            },
        ),
    ]
