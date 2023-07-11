#from cats.views import AchievementViewSet, CatViewSet
from django.conf import settings
from django.urls import include, path
from rest_framework import routers
from recipes.views import FavoriteViewSet, IngredientViewSet, RecipeViewSet, TagViewSet

router = routers.DefaultRouter()
#favorite_router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

router.register('recipes/(?P<id>[^/.]+)/favorite', FavoriteViewSet, basename='favorite')
router.register('tags', TagViewSet, basename='tags')
#router.register('users/subscriptions', SubscriptionsViewSet, basename='subscriptions')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    
    path('', include(router.urls)),
    #path('recipes/', include(favorite_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
