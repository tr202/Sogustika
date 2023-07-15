from django.contrib.auth import authenticate

from rest_framework import serializers

from djoser.conf import settings
from rest_framework.fields import empty

from recipes.models import Recipe
from users.models import AppUser, FavoriteUser


from djoser.serializers import TokenCreateSerializer, UserSerializer

        
class AppUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    
    def get_is_subscribed(self, obj):
        return obj.is_subscribed 
    
    class Meta:
        model = AppUser
        fields = settings.DEFAULT_USER_SERIALIZER_FIELDS + ('is_subscribed', )
        read_only_fields = (settings.LOGIN_FIELD,)


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscriptionsSerializer(AppUserSerializer):
    recipes = RecipeSerializer(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    def get_recipes_count(self, obj):
        return obj.recipes_count
    class Meta:
        model = AppUser
        fields = settings.DEFAULT_USER_SERIALIZER_FIELDS + ('is_subscribed', 'recipes', 'recipes_count', )
        


class AppTokenCreateSerializer(TokenCreateSerializer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.fields[settings.APP_LOGIN_FIELD] = serializers.CharField(required=False)

    def validate(self, attrs):
        password = attrs.get("password")
        params = {settings.APP_LOGIN_FIELD: attrs.get(settings.APP_LOGIN_FIELD)}
        self.user = authenticate(
            request=self.context.get("request"), **params, password=password
        )
        if not self.user:
            self.user = AppUser.objects.filter(**params).first()
            if self.user and not self.user.check_password(password):
                self.fail("invalid_credentials")
        if self.user and self.user.is_active:
            return attrs
        self.fail("invalid_credentials")
