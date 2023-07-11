from rest_framework.decorators import action
from rest_framework import filters, viewsets, status
from rest_framework import pagination
from rest_framework import permissions as drf_permission
from rest_framework.response import Response

from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend


from .models import (MeasurementUnit,
                     Ingredient,
                     Tag,
                     TagRecipe,
                     Recipe,
                     RecipeIngredient,
                     FavoriteRecipe,
                     FavoriteUser,
                     ShoppingCart)
from .serializers import FavoriteRecipeSerializer, IngredientSerializer, RecipeSerializer, TagSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset  = Tag.objects.all()
    #pagination_class = PageNumberPagination
    permission_classes = (drf_permission.AllowAny,)
    serializer_class = TagSerializer
    
class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    #pagination.PageNumberPagination.page_size = 'limit'
    permission_classes = (drf_permission.AllowAny,)

class RecipePagination(pagination.PageNumberPagination):
    page = 10
    page_size_query_param = 'limit'
    max_page_size = 100

FILTER_TAG_FIELD = 'tags'
FILTER_FAVORITE_FIELD = 'is_favorited'

def get_recipe_queryset(view, queryset):
    request_dict = dict(view.request.GET)
    lookup_tags = request_dict.get(FILTER_TAG_FIELD)
    is_favorited = request_dict.get(FILTER_FAVORITE_FIELD)
    if lookup_tags and is_favorited:
        favorite_queryset = FavoriteRecipe.objects.filter(user = view.request.user)
        queryset = queryset.filter(tags__slug__in = lookup_tags, favoriterecipe__in = favorite_queryset).distinct().order_by('-pub_date')
    elif lookup_tags:
        queryset = queryset.filter(tags__slug__in = lookup_tags).distinct().order_by('-pub_date')
    else:
        queryset = []
    return queryset
        

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = RecipePagination
    permission_classes = (drf_permission.AllowAny,)
    serializer_class = RecipeSerializer
    
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk is None:
            self.queryset = get_recipe_queryset
        return super().dispatch(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset(self, Recipe.objects.all())
        return super().list(request, *args, **kwargs)

'''
class CreateModelMixin:
    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
'''


class FavoriteViewSet(viewsets.ModelViewSet):
    lookup_fields = ('id',)
    queryset = FavoriteRecipe.objects.all()
    permission_classes = (drf_permission.AllowAny,)
    
    def create(self, request, *args, **kwargs):
        recipe = Recipe.objects.get(id=kwargs.pop('id'))
        serializer = FavoriteRecipeSerializer(recipe)
        FavoriteRecipe.objects.create(user = request.user, recipe = recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED,)
    
    
    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        recipe = Recipe.objects.get(id=kwargs.pop('id'))
        user = request.user
        FavoriteRecipe.objects.filter(user = user, recipe = recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    