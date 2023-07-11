import base64

from django.core.files.base import ContentFile

from rest_framework.fields import CurrentUserDefault
from rest_framework import serializers
from recipes.models import FavoriteRecipe, MeasurementUnit, Ingredient, Tag, TagRecipe, Recipe, RecipeIngredient
from users.models import AppUser


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
       
class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.SlugRelatedField(queryset=MeasurementUnit.objects.all(), slug_field='unit')
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ('email','id', 'username', 'first_name', 'last_name',)

class RecipeSerializer(serializers.ModelSerializer):
    author = AppUserSerializer()
    ingredients = IngredientSerializer(many=True,)
    image = Base64ImageField(required=True, allow_null=False)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    
    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        return 1 if user.is_authenticated and FavoriteRecipe.objects.filter(user=user, recipe=obj) else 0
        
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'name', 'image', 'text', 'cooking_time',)

