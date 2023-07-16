from django.urls import include, path

from rest_framework import routers

from api.views import (IngredientViewSet,
                       FavoriteViewSet,
                       RecipeViewSet,
                       ShoppingCartViewSet,
                       TagViewSet)
from users.views import AppUserViewSet, SubscribeViewSet, SubscriptionsViewSet

router = routers.DefaultRouter()

router.register(
    'recipes/(?P<id>[^/.]+)/favorite',
    FavoriteViewSet,
    basename='favorite'
)
router.register(
    'recipes/(?P<id>[^/.]+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart'
)
router.register(
    'users/(?P<id>[^/.]+)/subscribe',
    SubscribeViewSet,
    basename='subscribe'
)
router.register(
    'users/subscriptions',
    SubscriptionsViewSet,
    basename='subscriptions'
)
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', AppUserViewSet, basename='app_users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
