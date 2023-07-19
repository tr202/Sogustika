# Generated by Django 3.2 on 2023-07-18 18:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('recipes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingcart',
            name='byer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='byer_recipe', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_byer', to='recipes.recipe'),
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_recipe', to='recipes.ingredient'),
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredient', to='recipes.recipe'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='recipes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipe_ingredients', through='recipes.RecipeIngredient', to='recipes.Ingredient'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipe_tag', through='recipes.TagRecipe', to='recipes.Tag'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ingredient_unit', to='recipes.measurementunit'),
        ),
        migrations.AddField(
            model_name='favoriterecipe',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recipe_favorite', to='recipes.recipe'),
        ),
        migrations.AddField(
            model_name='favoriterecipe',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owner_recipe_favor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('byer', 'recipe'), name='no_double_recipe'),
        ),
        migrations.AddConstraint(
            model_name='favoriterecipe',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='no_double_favorite_recipe'),
        ),
    ]