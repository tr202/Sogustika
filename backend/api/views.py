from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef, Value
from django.http import FileResponse
from django_filters import rest_framework as dj_filters

from djoser.views import UserViewSet as ViewSet

from rest_framework import filters
from rest_framework import permissions as drf_permission
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import RecipeFilterSet
from api.pagination import Pagination
from api.serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                             RecipeCreateUpdateSerializer, RecipeSerializer,
                             SubscriptionsSerializer, TagSerializer,
                             UserSerializer)
from api.utils import get_pdf
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import Subscribtion

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (drf_permission.AllowAny,)
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().select_related(
        'measurement_unit')
    serializer_class = IngredientSerializer
    permission_classes = (drf_permission.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = Pagination
    permission_classes = (drf_permission.AllowAny,)
    filter_backends = (dj_filters.DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.select_related(
            'author',
        ).prefetch_related(
            'ingredients',
            'tags',
            'recipe_ingredients__ingredient',
            'ingredients__measurement_unit',
            'author__subscriber'
        ).annotate(
            is_favorited=Exists(
                FavoriteRecipe.objects.filter(
                    recipe_id=OuterRef('pk'),
                    user=user.id)),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    recipe_id=OuterRef('pk'),
                    byer=user.id)),
            is_subscribed=Exists(
                Subscribtion.objects.filter(
                    user_id=OuterRef('pk'),
                    subscriber=user.id)),
        )
        return queryset

    @action(methods=('get', ),
            detail=False,
            permission_classes=(drf_permission.IsAuthenticated, ))
    def download_shopping_cart(self, request, *args, **kwargs):
        return FileResponse(
            get_pdf(self.request.user),
            as_attachment=True,
            filename="shopping-list.pdf"
        )

    def get_serializer_class(self):
        if self.action in ('update',
                           'create',
                           'partial_update',
                           ):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    lookup_fields = ('id',)
    queryset = FavoriteRecipe.objects.all()
    permission_classes = (drf_permission.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        recipe = Recipe.objects.get(id=kwargs.pop('id'))
        serializer = FavoriteRecipeSerializer(recipe)
        FavoriteRecipe.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED,)

    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        FavoriteRecipe.objects.filter(
            user=request.user,
            recipe_id=kwargs.pop('id')).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    lookup_fields = ('id',)
    queryset = ShoppingCart.objects.all()
    permission_classes = (drf_permission.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        recipe = Recipe.objects.get(id=kwargs.pop('id'))
        serializer = FavoriteRecipeSerializer(recipe)
        ShoppingCart.objects.create(byer=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED,)

    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        ShoppingCart.objects.filter(
            byer=request.user,
            recipe_id=kwargs.pop('id')).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(ViewSet):
    pagination_class = Pagination
    permission_classes = (drf_permission.IsAuthenticated, )
    serializer_class = UserSerializer

    def dispatch(self, request, *args, **kwargs):
        self.pk = kwargs.get('id')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            favorite_users_queryset = Subscribtion.objects.filter(
                user=OuterRef('pk'),
                subscriber=self.request.user)
            users_queryset = User.objects.annotate(
                is_subscribed=Exists(
                    favorite_users_queryset))
        elif self.pk:
            users_queryset = User.objects.filter(
                pk=self.pk).annotate(
                    is_subscribed=Value(False))
        return users_queryset

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = (drf_permission.AllowAny, )
        return super().get_permissions()


class SubscriptionsViewSet(viewsets.ModelViewSet):
    permission_classes = (drf_permission.IsAuthenticated,)
    pagination_class = Pagination
    serializer_class = SubscriptionsSerializer

    def get_queryset(self):
        favorite_users_queryset = Subscribtion.objects.filter(
            user=OuterRef('pk'),
            subscriber=self.request.user)
        users_queryset = User.objects.annotate(
            is_subscribed=Exists(
                favorite_users_queryset)).filter(
                    is_subscribed=True)
        users_queryset = users_queryset .annotate(
            recipes_count=Count('recipes'))
        return users_queryset


class SubscribeViewSet(viewsets.ModelViewSet):
    lookup_fields = ('id',)
    permission_classes = (drf_permission.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        subscriber_id = request.user.pk
        id = kwargs.pop('id')
        user = User.objects.filter(id=id)
        Subscribtion.objects.create(
            user_id=id,
            subscriber_id=subscriber_id)
        favorite = Subscribtion.objects.filter(
            user_id=id,
            subscriber_id=subscriber_id)
        user = user.annotate(is_subscribed=Exists(favorite)).get(id=id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED,)

    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        user_id = kwargs.pop('id')
        subscriber_id = request.user.pk
        Subscribtion.objects.filter(
            user_id=user_id,
            subscriber_id=subscriber_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
