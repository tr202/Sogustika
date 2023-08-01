from django.urls import include, path
from rest_framework import routers

from api.views import (
    FavoriteViewSet,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    SubscriptionsViewSet,
    TagViewSet,
)

router = routers.DefaultRouter()

router.register(
    "recipes/(?P<id>[^/.]+)/favorite", FavoriteViewSet, basename="favorite"
)
router.register(
    "recipes/(?P<id>[^/.]+)/shopping_cart",
    ShoppingCartViewSet,
    basename="shopping_cart",
)

router.register("recipes", RecipeViewSet, basename="recipes")

router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("tags", TagViewSet, basename="tags")
subscribe_urls = [
    path("subscriptions/", SubscriptionsViewSet.as_view({"get": "list"})),
    path(
        "<int:id>/subscribe/",
        SubscriptionsViewSet.as_view(
            {"post": "subscribe", "delete": "unsubscribe"}
        ),
    ),
]

urlpatterns = [
    path("users/", include(subscribe_urls)),
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
