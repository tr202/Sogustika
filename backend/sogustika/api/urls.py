#from cats.views import AchievementViewSet, CatViewSet
from django.conf import settings
from django.urls import include, path
from rest_framework import routers
from recipes.views import FavoriteViewSet, IngredientViewSet, RecipeViewSet, TagViewSet, ShoppingCartViewSet
from users.views import SubscribeViewSet, SubscriptionsViewSet, AppUserViewSet

router = routers.DefaultRouter()
users_router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes/(?P<id>[^/.]+)/favorite', FavoriteViewSet, basename='favorite')
router.register('tags', TagViewSet, basename='tags')
router.register('users/(?P<id>[^/.]+)/subscribe', SubscribeViewSet, basename='subscribe')
router.register('users/subscriptions', SubscriptionsViewSet, basename='subscriptions')
router.register('users', AppUserViewSet, basename='app_users')
router.register('recipes/(?P<id>[^/.]+)/shopping_cart', ShoppingCartViewSet, basename='shopping_cart')



urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
