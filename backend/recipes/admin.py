from django.contrib import admin
from django.contrib.auth import get_user_model

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class IngredientInline(admin.TabularInline):
    model = Ingredient
    readonly_fields = ("id",)
    extra = 1


class RecipeIngredientInline(admin.TabularInline):
    inlines = (IngredientInline,)
    model = RecipeIngredient
    readonly_fields = ("id",)
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "measurement_unit",
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = (
        "id",
        "name",
        "author",
        "text",
        "get_favorited_count",
        "cooking_time",
        "pub_date",
        "get_tags",
    )

    list_filter = (
        "name",
        "author",
        "tags",
    )

    def get_favorited_count(self, recipe):
        return User.objects.filter(favorites=recipe).count()

    get_favorited_count.__name__ = "добавлен в избранное"

    def get_tags(self, recipe):
        recipe_tags = recipe.tags.all()
        tags = tuple(map(lambda x: x.name, recipe_tags))
        return tags

    get_tags.__name__ = "теги"
