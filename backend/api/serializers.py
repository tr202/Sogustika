import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        return data

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )
        read_only_fields = (
            "name",
            "color",
            "slug",
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class UserSerializer(UserSerializer, UserCreateSerializer):
    is_subscribed = serializers.ReadOnlyField(default=False)

    class Meta:
        model = User
        short_fields = (
            "email",
            "username",
            "first_name",
            "last_name",
        )
        UserCreateSerializer.Meta.fields += short_fields
        fields = short_fields + (
            "id",
            "is_subscribed",
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient_id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    image = serializers.ImageField()
    ingredients = RecipeIngredientSerializer(
        source="recipe_ingredients", many=True
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.BooleanField(
        default=False,
    )
    is_in_shopping_cart = serializers.BooleanField(default=False)

    def get_author(self, obj):
        serialiser = UserSerializer()
        obj.author.is_subscribed = obj.is_subscribed
        return serialiser.to_representation(obj.author)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("__all__",)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        data["ingredient_id"] = data.pop("id")
        return data

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "amount",
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(allow_null=False, required=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientsSerializer(many=True)

    def set_ingredients(self, ingredients, instance):
        data = list(map(lambda x: dict(x, recipe=instance), ingredients))
        objects_set = map(lambda x: RecipeIngredient(**x), data)
        return RecipeIngredient.objects.bulk_create(objects_set)

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        instance.tags.set(tags)
        self.set_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance = Recipe.objects.create(
            **validated_data,
            author=self.context.get("request").user,
        )
        instance.tags.set(tags)
        self.set_ingredients(ingredients, instance)
        return instance

    def validate(self, data):
        errors = {}
        if data.get("cooking_time") <= 0:
            errors[
                "cooking_time"
            ] = "Время приготовления должно быть больше нуля"
        ingredients = data.get("ingredients")

        ids_ingredients = list(
            map(lambda x: x.get("ingredient_id"), ingredients)
        )
        ingredients_error_list = []
        if len(ids_ingredients) > len(set(ids_ingredients)):
            ingredients_error_list.append("Ингредиенты не должны повторяться")
        for ingredient in ingredients:
            if int(ingredient.get("amount")) <= 0:
                ingredients_error_list.append(
                    {
                        Ingredient.objects.get(
                            id=ingredient.get("ingredient_id")
                        ).name: "Количество должно быть больше нуля"
                    }
                )
        if len(ingredients_error_list) > 0:
            errors["ingredients"] = ingredients_error_list
        if len(data.get("tags")) <= 0:
            errors["tags"] = "Теги обязательны\n"
        if errors:
            js = str(errors)
            print(js)
            raise serializers.ValidationError(js)
        return data

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "tags",
            "cooking_time",
            "text",
            "image",
            "ingredients",
        )


class UserRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class SubscriptionsSerializer(UserSerializer):
    recipes = UserRecipeSerializer(read_only=True, many=True)
    is_subscribed = serializers.BooleanField(default=False)
    recipes_count = serializers.SerializerMethodField()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
