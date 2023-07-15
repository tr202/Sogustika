import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


from itertools import chain
from pprint import PrettyPrinter, pprint
from typing import Any
from rest_framework.decorators import action
from rest_framework import filters, viewsets, status
from rest_framework import pagination
from rest_framework import permissions as drf_permission
from rest_framework.response import Response

from django.db.models import Exists, Value, OuterRef, Subquery, Count, Prefetch,Sum, Manager
from django.contrib.auth.models import AnonymousUser

from django_filters.rest_framework import DjangoFilterBackend


from .models import (MeasurementUnit,
                     Ingredient,
                     Tag,
                     TagRecipe,
                     Recipe,
                     RecipeIngredient,
                     FavoriteRecipe,
                     ShoppingCart)
from users.models import FavoriteUser, AppUser
from .serializers import FavoriteRecipeSerializer, IngredientSerializer, RecipeSerializer, TagSerializer, RecipeCreateUpdateSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset  = Tag.objects.all()
    permission_classes = (drf_permission.AllowAny,)
    serializer_class = TagSerializer
    def dispatch(self, request, *args, **kwargs):
        print('recipe')
        return super().dispatch(request, *args, **kwargs)

class IngredientFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_param = request.GET.get('name')
        queryset = queryset.filter(name__startswith=search_param)
        return queryset
        
    
class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().select_related('measurement_unit')
    serializer_class = IngredientSerializer
    permission_classes = (drf_permission.AllowAny,)
    filter_backends = [IngredientFilter]
    search_fields = ('name',)


class RecipePagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'limit'
    max_page_size = 100

FILTER_TAG_FIELD = 'tags'
FILTER_FAVORITE_FIELD = 'is_favorited'
FILTER_AUTHOR_FIELD = 'author'
LOOKUP_FIELDS = ('tags', 'is_favorited', 'author')
FILTER_SHOPPING_CART = 'is_in_shopping_cart'

############# pdf
TITLE = 'Список покупок'
def drawMyRuler(pdf):
    pdf.drawString(100,810, 'x100')
    pdf.drawString(200,810, 'x200')
    pdf.drawString(300,810, 'x300')
    pdf.drawString(400,810, 'x400')
    pdf.drawString(500,810, 'x500')
    
    pdf.drawString(10,100, 'x100')
    pdf.drawString(10,200, 'x200')
    pdf.drawString(10,300, 'x300')
    pdf.drawString(10,400, 'x400')
    pdf.drawString(10,500, 'x500')
    pdf.drawString(10,600, 'x600')
    pdf.drawString(10,700, 'x700')
    pdf.drawString(10,800, 'x800')
    
pdfmetrics.registerFont(
    TTFont('beer-money12', 'recipes/fonts/beer-money12.ttf')
) 
pdfmetrics.registerFont(
    TTFont('dewberry-bold-italic.ttf', 'recipes/fonts/dewberry-bold-italic.ttf')
)  

class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = RecipePagination
    permission_classes = (drf_permission.AllowAny,)
    
    @action(methods=('get', ), detail=False, permission_classes=(drf_permission.IsAuthenticated, ))
    def download_shopping_cart(self,request,*args,**kwargs):
        query = RecipeIngredient.objects.filter(recipe_id__in=ShoppingCart.objects.filter(byer=self.request.user).values('recipe_id')).values('ingredient__name','ingredient__measurement_unit__unit', 'ingredient__measurement_unit__counted').order_by('ingredient_id').annotate(total=Sum('amount'))
        print(query)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        #drawMyRuler(p)
        #p.setFillColorRGB
        
        p.setFont('beer-money12', 36)
        p.setTitle('Список покупок')
        p.drawCentredString(300, 750, 'Список покупок.')
        p.line(80,700,480,700)
        p.setFont('dewberry-bold-italic.ttf', 20)
        position_x = 100
        start_position_y = 650
        step_position_y = 25
        for ingredient in query:
            print(ingredient.get('ingredient__name'), ingredient.get('total'))
            name = ingredient.get('ingredient__name')
            amount = ingredient.get('total')
            unit = ingredient.get('ingredient__measurement_unit__unit')
            counted = ingredient.get('ingredient__measurement_unit__counted')
            if not counted:
                amount=''
            ingredient_string = (name + ' ' + str(amount)+ unit) 
            p.drawString(position_x, start_position_y, ingredient_string)
            start_position_y -=step_position_y
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="shopping-list.pdf")
    
    def get_queryset(self):
        queryset = Recipe.objects.annotate(is_favorited=Value(False), is_subscribed=Value(False), is_in_shopping_cart=Value(False)).select_related('author').prefetch_related('recipe_ingredient').prefetch_related('tags').prefetch_related('ingredients')#Prefetch('ingredients', queryset=Ingredient.objects.select_related('measurement_unit')))
        request_dict = dict(self.request.GET)
        user = self.request.user if self.request.user.is_authenticated else None
        def filter_tags(queryset):
            if ({'page', 'limit'} & set(request_dict)) and not 'is_in_shopping_cart' in request_dict:
                lookup_tags = request_dict.get(FILTER_TAG_FIELD)
                queryset = queryset.filter(tags__slug__in = lookup_tags).distinct().order_by('-pub_date') if lookup_tags else Recipe.objects.none()
            return queryset
        def filter_user(queryset):
            if user:
                is_favorited = request_dict.get(FILTER_FAVORITE_FIELD)
                author = request_dict.get(FILTER_AUTHOR_FIELD)
                shopping_cart = request_dict.get(FILTER_SHOPPING_CART)
                shopping_cart_queryset = ShoppingCart.objects.filter(recipe_id=OuterRef('pk'), byer=user)
                favorite_queryset = FavoriteRecipe.objects.filter(recipe_id=OuterRef('pk'), user = user)
                favorite_users_queryset = FavoriteUser.objects.filter(user_id=OuterRef('author'), subscriber = user)
                queryset = queryset.annotate(is_subscribed=Exists(favorite_users_queryset))
                queryset = queryset.annotate(is_favorited=Exists(favorite_queryset))
                queryset = queryset.annotate(is_in_shopping_cart=Exists(shopping_cart_queryset))
                queryset = queryset = queryset.filter(is_favorited=True) if is_favorited else queryset
                queryset = queryset.filter(author__in = author) if author else queryset
                queryset = queryset.filter(is_in_shopping_cart = True) if shopping_cart else queryset
            return queryset
        queryset = filter_tags(queryset)
        queryset = filter_user(queryset)
        return queryset

    def get_serializer_class(self):
        if self.action in ('update', 'create','partial_update',) and self.request.user.is_authenticated:
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
        FavoriteRecipe.objects.create(user = request.user, recipe = recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED,)
    
    
    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        FavoriteRecipe.objects.filter(user = request.user, recipe_id = kwargs.pop('id')).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ShoppingCartViewSet(viewsets.ModelViewSet):
    lookup_fields = ('id',)
    queryset = ShoppingCart.objects.all()
    permission_classes = (drf_permission.IsAuthenticated,)
    
    def create(self, request, *args, **kwargs):
        recipe = Recipe.objects.get(id=kwargs.pop('id'))
        serializer = FavoriteRecipeSerializer(recipe)
        ShoppingCart.objects.create(byer = request.user, recipe = recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED,)
    
    
    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        ShoppingCart.objects.filter(byer = request.user, recipe_id = kwargs.pop('id')).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

  
