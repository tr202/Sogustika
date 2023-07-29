import base64

from django.db import transaction
from django.core.files.base import ContentFile

from rest_framework import serializers
from recipes.models import (Ingredient,
                            MeasurementUnit,
                            RecipeIngredient,
                            Recipe,
                            Tag,)
from users.models import AppUser


class TagSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        return data
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = ('name', 'color', 'slug',)
        

class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.SlugRelatedField(
        queryset=MeasurementUnit.objects.all(),
        slug_field='unit'
    )
    
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class AppUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField()
   
    class Meta:
        model = AppUser
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient_id')
    name = serializers.CharField()
    measurement_unit = serializers.CharField()
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)

        
class RecipeSerializer(serializers.ModelSerializer):
    author = AppUserSerializer()
    image = serializers.ImageField()
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredient',
        many=True
    )
    tags = TagSerializer(many=True,)
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()
    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time',
                  )
        read_only_fields = ('__all__',)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        return data

    class Meta:
        model = RecipeIngredient
        fields =  ('id', 'amount',)

class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(allow_null=False, required=True)
    tags = TagSerializer(many=True, )
    ingredients = RecipeIngredientsSerializer(many=True)

    def set_ingredients(self, ingredients, instance):
        return RecipeIngredient.objects.bulk_create(
            RecipeIngredient(ingredient_id=ingredient.get('id'),
                             amount=ingredient.get('amount'),
                             recipe=instance) for ingredient in ingredients)

    @transaction.atomic    
    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        print(ingredients)
        self.set_ingredients(ingredients, instance)
        return super().update(instance, validated_data)
    
    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = Recipe.objects.create(
            **validated_data,
            author=self.context.get('request').user,
            )
        instance.tags.set(tags)
        self.set_ingredients(ingredients, instance)
        return instance


    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'tags',
                  'cooking_time',
                  'text',
                  'image',
                  'ingredients',)
        
