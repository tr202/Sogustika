from django.contrib import admin
from recipes.models import (FavoriteRecipe,
                            Ingredient,
                            MeasurementUnit,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag,
                            TagRecipe)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'unit',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_measurement_unit')

    def get_measurement_unit(self, ingredient):
        return ingredient.measurement_unit.unit


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'author',
                    'text',
                    'get_favorited_count',
                    'cooking_time',
                    'pub_date',
                    'get_tags',)

    list_filter = ('name', 'author', 'tags',)

    def get_favorited_count(self, recipe):
        return FavoriteRecipe.objects.filter(recipe=recipe).count()
    get_favorited_count.__name__ = 'добавлен в избранное'

    def get_tags(self, recipe):
        recipe_tags = recipe.tags.all()
        print(recipe_tags)
        tags = tuple(map(lambda x: x.name, recipe_tags))
        print(tags)
        return tags
    get_tags.__name__ = 'теги'


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass
