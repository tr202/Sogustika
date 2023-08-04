# Generated by Django 3.2 on 2023-08-04 13:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0002_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="recipe",
            constraint=models.CheckConstraint(
                check=models.Q(cooking_time__gte=0),
                name="Cookong time most be more than zero",
            ),
        ),
        migrations.AddConstraint(
            model_name="recipe",
            constraint=models.UniqueConstraint(
                fields=("author", "name"), name="No doule recipe name"
            ),
        ),
        migrations.AddConstraint(
            model_name="recipeingredient",
            constraint=models.CheckConstraint(
                check=models.Q(amount__gte=0),
                name="Amount most be more than zero",
            ),
        ),
        migrations.AddConstraint(
            model_name="recipeingredient",
            constraint=models.UniqueConstraint(
                fields=("recipe", "ingredient"), name="no_double_ingredient"
            ),
        ),
    ]
