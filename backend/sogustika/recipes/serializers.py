import base64

from django.core.files.base import ContentFile

from rest_framework.fields import CurrentUserDefault, empty
from rest_framework import serializers
from recipes.models import FavoriteRecipe, MeasurementUnit, Ingredient, Tag, TagRecipe, Recipe, RecipeIngredient
from users.models import AppUser, FavoriteUser


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)

class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.SlugRelatedField(queryset=MeasurementUnit.objects.all(), slug_field='unit')
    
    def to_representation(self, instance):
        #ins = instance.get('q1')
        #print(instance.recipe_ingredient)
        return super().to_representation(instance)
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)           

class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    def get_id(self,obj):
        return obj.ingredient.id
    name = serializers.SerializerMethodField()
    def get_name(self,obj):
        return obj.ingredient.name
    measurement_unit = serializers.SerializerMethodField()
    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit.unit
    amount= serializers.SerializerMethodField()
    def get_amount(self, obj):
        if obj.ingredient.measurement_unit.counted:
            return obj.amount
            
        else:
            return ''
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit','amount')


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

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    
    def get_is_subscribed(self, obj):
        return obj.is_subscribed
    
    class Meta:
        model = AppUser
        fields = ('email','id', 'username', 'first_name', 'last_name', 'is_subscribed',)


class TagField(serializers.RelatedField):

    def to_representation(self, obj):
        return {
            'id': obj.id,
            'name': obj.name,
        }

    def to_internal_value(self, data):
        try:
            try:
                obj_id = data
                #return obj_id
                return Tag.objects.get(id=obj_id)
            except KeyError:
                raise serializers.ValidationError(
                    'id is a required field.'
                )
            except ValueError:
                raise serializers.ValidationError(
                    'id must be an integer.'
                )
        except Tag.DoesNotExist:
            raise serializers.ValidationError(
            'Obj does not exist.'
            )

              
class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    image = serializers.ImageField()
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True,)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    
    def get_ingredients(self, obj):
        serializer = IngredientSerializer(many=True, required=False,)
        #obj.ingredients.add(obj.recipe_ingredient)
        #ins = {'q1':obj.ingredients,'q2':obj.recipe_ingredient}
        serializer = RecipeIngredientSerializer(many=True, required=False,)
        return serializer.to_representation(obj.recipe_ingredient)
        
    def get_author(self, obj):
        serialiser = AppUserSerializer()
        obj.author.is_subscribed = obj.is_subscribed
        return  serialiser.to_representation(obj.author)
    
    def get_is_in_shopping_cart(self, obj):
        return obj.is_in_shopping_cart
    
    def get_is_favorited(self, obj):
        return obj.is_favorited
        
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',)
        read_only_fields = ('__all__',)


class IngredientField(serializers.RelatedField):
    def to_representation(self, value):
        value = 1
        return value
    def to_internal_value(self, data):
        ingredient = Ingredient.objects.get(pk=data.get('id'))
        amount = data.get('amount')
        return {'ingredient':ingredient, 'amount':amount}

class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(allow_null=False, required=True)
    tags = TagField(many=True, queryset = TagRecipe.objects.all())
    ingredients = IngredientField(many=True, queryset=RecipeIngredient.objects.all())
    
    def update(self, instance, validated_data):
        id = instance.id
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        if 'image' in validated_data.keys():
            image = validated_data.pop('image')
        else:
            image = Recipe.objects.get(id=id).image
        RecipeIngredient.objects.filter(recipe__id=id).delete()
        TagRecipe.objects.filter(recipe__id=id).delete()
        Recipe.objects.filter(id=id).delete()
        recipe = Recipe.objects.create(**validated_data, author = self.context.get('request').user, image=image, id=id)
        for tag in tags:
            TagRecipe.objects.create(tag=tag,recipe=recipe)
        for ingredient in ingredients:
            amount=ingredient.get('amount')
            amount = amount if isinstance(amount, int) else None
            RecipeIngredient.objects.create(ingredient=ingredient.get('ingredient'),amount=amount,recipe=recipe) 
        return recipe
    
    def create(self, validated_data, instance=None):    
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data, author = self.context.get('request').user)
        for tag in tags:
            TagRecipe.objects.create(tag=tag,recipe=recipe)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(ingredient=ingredient.get('ingredient'),amount=ingredient.get('amount'),recipe=recipe) 
        return recipe
        
    class Meta:
        model = Recipe
        fields = ('name','tags','cooking_time', 'text', 'image','ingredients', )        
        
