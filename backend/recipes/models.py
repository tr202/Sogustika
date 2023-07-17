from django.db import models
from django.core.exceptions import ValidationError

from recipes.utils import slugify
from users.models import AppUser


class MeasurementUnit(models.Model):
    unit = models.CharField(max_length=10, null=False, unique=True,)
    counted = models.BooleanField(null=False,)

    class Meta:
        verbose_name_plural = 'единицы меры'
        verbose_name = 'меру'
        ordering = ('unit',)

    def __str__(self):
        return str(self.id) + ' ' + self.unit + ' ' + str(self.counted)


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=False, blank=False)
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        null=True,
        on_delete=models.SET_NULL,
        related_name='ingredient_unit',
    )

    class Meta:
        verbose_name_plural = 'ингредиенты'
        verbose_name = 'игредиент'
        ordering = ('name',)

    def __str__(self):
        return (str(self.id)
                + ' '
                + self.name
                + ' '
                + self.measurement_unit.unit)


class Tag(models.Model):
    name = models.CharField(max_length=200,)
    color = models.CharField(max_length=7)
    slug = models.SlugField(
        'Slug-тега',
        unique=True,
        blank=False,
        max_length=200,
        help_text=(
            'Используйте только латиницу,'
            + 'цифры, дефисы и знаки подчёркивания'),
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:200]
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Теги'
        verbose_name = 'тег'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    pub_date = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag,
                                  through='TagRecipe',
                                  related_name='recipe_tag',)
    author = models.ForeignKey(AppUser,
                               on_delete=models.SET_DEFAULT,
                               default=AppUser.objects.get(
                                   username='sogustika').pk,
                               null=False,
                               related_name='recipes',)

    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         related_name='recipe_ingredients',)
    name = models.CharField(max_length=200, blank=False, null=False,)
    image = models.ImageField(upload_to='recipes/images/',
                              null=True,
                              default=None,)
    text = models.TextField(null=False,)
    cooking_time = models.SmallIntegerField()

    class Meta:
        verbose_name_plural = 'рецепты'
        verbose_name = 'рецепт'
        ordering = ('-pub_date',)

    def __str__(self):
        return (self.name
                + ' '
                + self.author.username
                + ' '
                + str(self.cooking_time)
                + ' '
                + self.text[:100])


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            related_name='tag_recipe',)
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipe_tag',)

    class Meta:
        ordering = ('recipe',)

    def __str__(self):
        return self.tag.name + ' ' + self.recipe.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipe_ingredient',)
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='ingredient_recipe')
    amount = models.SmallIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        counted = self.ingredient.measurement_unit.counted
        if counted:
            try:
                int(self.amount)
            except ValueError:
                raise ValidationError('Can not cast amount to int')
        else:
            self.amount = None
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('recipe',)

    def __str__(self):
        return (self.recipe.name
                + ' '
                + self.ingredient.name
                + ' ' + str('amoumt')
                + self.ingredient.measurement_unit.unit)


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(AppUser,
                             on_delete=models.CASCADE,
                             null=True, related_name='owner_recipe_favor',)
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               null=True,
                               related_name='recipe_favorite',)

    class Meta:
        verbose_name_plural = 'Избранные рецепты'
        verbose_name = 'рецепт в избранном'
        constraints = (
            models.UniqueConstraint(
                name='no_double_favorite_recipe',
                fields=('user', 'recipe',)
            ),
        )
        ordering = ('recipe',)

    def __str__(self):
        return ('У '
                + self.user.username
                + ' в избранном рецепт '
                + self.recipe.name)


class ShoppingCart(models.Model):
    byer = models.ForeignKey(AppUser,
                             on_delete=models.CASCADE,
                             related_name='byer_recipe',)
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipe_byer',)

    class Meta:
        verbose_name_plural = 'корзины'
        verbose_name = 'корзину'
        constraints = (
            models.UniqueConstraint(
                name='no_double_recipe',
                fields=('byer', 'recipe',)
            ),
        )
        ordering = ('recipe',)

    def __str__(self):
        return (
            'У '
            + self.byer.username
            + ' в корзине рецепт '
            + self.recipe.name)
