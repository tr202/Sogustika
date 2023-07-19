from django.db.models import Exists, OuterRef, Sum, Value
from django.http import FileResponse

from rest_framework import filters, viewsets, status
from rest_framework import pagination
from rest_framework import permissions as drf_permission
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import (IngredientSerializer,
                             FavoriteRecipeSerializer,
                             RecipeCreateUpdateSerializer,
                             RecipeSerializer,
                             TagSerializer,)
from api.utils import get_pdf
from recipes.models import (FavoriteRecipe,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag)
from users.models import FavoriteUser

FILTER_TAG_FIELD = 'tags'
FILTER_FAVORITE_FIELD = 'is_favorited'
FILTER_AUTHOR_FIELD = 'author'
LOOKUP_FIELDS = ('tags', 'is_favorited', 'author')
FILTER_SHOPPING_CART = 'is_in_shopping_cart'


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (drf_permission.AllowAny,)
    serializer_class = TagSerializer


class IngredientFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_param = request.GET.get('name').lower()
        q_startwith = queryset.filter(name__startswith=search_param)
        queryset = queryset.annotate(
            start=Exists(q_startwith)).filter(
                name__icontains=search_param).order_by('start')
        return queryset


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().select_related(
        'measurement_unit')
    serializer_class = IngredientSerializer
    permission_classes = (drf_permission.AllowAny,)
    filter_backends = [IngredientFilter]
    search_fields = ('name',)


class RecipePagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'limit'
    max_page_size = 100


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = RecipePagination
    permission_classes = (drf_permission.AllowAny,)

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

    def get_queryset(self):
        queryset = Recipe.objects.annotate(
            is_favorited=Value(False),
            is_subscribed=Value(False),
            is_in_shopping_cart=Value(False)
        ).select_related(
            'author'
        ).prefetch_related(
            'recipe_ingredient'
        ).prefetch_related(
            'tags'
        ).prefetch_related(
            'ingredients'
        )
        request_dict = dict(self.request.GET)
        user = (self.request.user
                if self.request.user.is_authenticated else None)

        def filter_tags(queryset):
            param_exists = ({'page', 'limit'} & set(request_dict))
            if param_exists and not ('is_in_shopping_cart' in request_dict):
                lookup_tags = request_dict.get(FILTER_TAG_FIELD)
                queryset = queryset.filter(
                    tags__slug__in=lookup_tags
                ).distinct().order_by(
                    '-pub_date') if lookup_tags else Recipe.objects.none()
            return queryset

        def filter_user(queryset):
            if user:
                is_favorited = request_dict.get(FILTER_FAVORITE_FIELD)
                author = request_dict.get(FILTER_AUTHOR_FIELD)
                shopping_cart = request_dict.get(FILTER_SHOPPING_CART)
                shopping_cart_queryset = ShoppingCart.objects.filter(
                    recipe_id=OuterRef('pk'),
                    byer=user)
                favorite_queryset = FavoriteRecipe.objects.filter(
                    recipe_id=OuterRef('pk'),
                    user=user)
                favorite_users_queryset = FavoriteUser.objects.filter(
                    user_id=OuterRef('author'),
                    subscriber=user)
                queryset = queryset.annotate(
                    is_subscribed=Exists(favorite_users_queryset))
                queryset = queryset.annotate(
                    is_favorited=Exists(favorite_queryset))
                queryset = queryset.annotate(
                    is_in_shopping_cart=Exists(shopping_cart_queryset))
                queryset = queryset.filter(
                    is_favorited=True) if is_favorited else queryset
                queryset = queryset.filter(
                    author__in=author) if author else queryset
                queryset = queryset.filter(
                    is_in_shopping_cart=True) if shopping_cart else queryset
            return queryset
        queryset = filter_tags(queryset)
        queryset = filter_user(queryset)
        return queryset

    def get_serializer_class(self):
        if self.action in ('update',
                           'create',
                           'partial_update',
                           ) and self.request.user.is_authenticated:
            return RecipeCreateUpdateSerializer
        else:
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
