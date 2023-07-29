from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef,Prefetch, Sum, Value
from django.http import FileResponse

from rest_framework import filters, viewsets, status
from rest_framework import permissions as drf_permission
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters import rest_framework as dj_filters

from api.pagination import RecipePagination
from api.serializers import (IngredientSerializer,
                             FavoriteRecipeSerializer,
                             RecipeCreateUpdateSerializer,
                             RecipeSerializer,
                             TagSerializer,)
from api.utils import get_pdf
from recipes.models import (FavoriteRecipe,
                            Ingredient,
                            MeasurementUnit,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag,
                            TagRecipe,)
from users.models import FavoriteUser

AppUser = get_user_model()

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (drf_permission.AllowAny,)
    serializer_class = TagSerializer


class IngredientFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_param = request.GET.get('name')
        queryset = queryset.filter(name__istartswith=search_param)
        return queryset


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().select_related(
        'measurement_unit')
    serializer_class = IngredientSerializer
    permission_classes = (drf_permission.AllowAny,)
    filter_backends = (IngredientFilter,)
    search_fields = ('name',)

class RecipeFilterSet(dj_filters.FilterSet):
    tags = dj_filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = dj_filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = dj_filters.BooleanFilter(method='get_is_in_shopping_cart')
    
    def get_is_in_shopping_cart(self, queryset, name, value):
        return queryset.filter(is_in_shopping_cart=True) if value else queryset
        
    def get_is_favorited(self, queryset, name, value):
        return queryset.filter(is_favorited=True) if value else queryset
    
    class Meta:
        model = Recipe
        fields = ('author',)

class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = RecipePagination
    permission_classes = (drf_permission.AllowAny,)
    filter_backends = (dj_filters.DjangoFilterBackend,)
    filterset_class = RecipeFilterSet
    
    def get_queryset(self):
        if self.action in ('update',
                           'create',
                           'partial_update',
                           ):
            return Recipe.objects.all()
        queryset = Recipe.objects.all()
        subquery_name = Ingredient.objects.filter(id=OuterRef('ingredient_id'))
        subquery_unit = Ingredient.objects.filter(
            id=OuterRef(OuterRef('ingredient_id'))).values('measurement_unit_id')[:1]
        queryset = queryset.prefetch_related(
            Prefetch(
            'recipe_ingredient',
            RecipeIngredient.objects.annotate(
                name=subquery_name.values('name'),
                measurement_unit=MeasurementUnit.objects.filter(
                    id=subquery_unit).values('unit'))))
        user = self.request.user
        if user.is_authenticated:
            return queryset.annotate(
                is_favorited=Exists(
                    FavoriteRecipe.objects.filter(
                        recipe_id=OuterRef('pk'),
                        user=user)),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        recipe_id=OuterRef('pk'),
                        byer=user))
            ).prefetch_related(
                Prefetch(
                    'author', AppUser.objects.annotate(
                        is_subscribed=Exists(
                            FavoriteUser.objects.filter(
                            user_id=OuterRef('pk'),
                            subscriber=user)))),
                    'tags',
                    'ingredients')
        return queryset.annotate(
            is_favorited=Value(False),
            is_in_shopping_cart=Value(False)
        ).prefetch_related(
            Prefetch(
                'author', AppUser.objects.annotate(
                    is_subscribed=Value(False))), 'tags')

    @action(methods=('get', ),
            detail=False,
            permission_classes=(drf_permission.IsAuthenticated, ))
    def download_shopping_cart(self, request, *args, **kwargs):
        query = RecipeIngredient.objects.filter(
            recipe_id__in=ShoppingCart.objects.filter(
                byer=self.request.user).values(
                    'recipe_id')
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit__unit',
            'ingredient__measurement_unit__counted'
        ).order_by(
            'ingredient_id'
        ).annotate(
            total=Sum('amount')
        )
        return FileResponse(
            get_pdf(query), as_attachment=True, filename="shopping-list.pdf")

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
