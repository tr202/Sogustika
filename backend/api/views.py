from api.filters import RecipeFilterSet
from api.pagination import Pagination
from api.serializers import (
    FavoriteRecipeSerializer,
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeSerializer,
    SubscriptionsSerializer,
    TagSerializer,
)
from api.utils import get_pdf
from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef
from django.http import FileResponse
from django_filters import rest_framework as dj_filters
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import filters, mixins
from rest_framework import permissions as drf_permission
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    permission_classes = (drf_permission.AllowAny,)
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (drf_permission.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = Pagination
    permission_classes = (drf_permission.AllowAny,)
    filter_backends = (dj_filters.DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Recipe.objects.all()
            .select_related(
                "author",
            )
            .prefetch_related(
                "ingredients",
                "tags",
            )
        )

        if user.is_authenticated:
            favorites = user.favorites.values("name")
            shoping_cart = user.shopping_cart.values("name")
            subscribes = user.subscriptions.values("username")
            queryset = queryset.annotate(
                is_subscribed=Exists(
                    subscribes.filter(username=OuterRef("author__username"))
                ),
                is_favorited=Exists(favorites.filter(name=OuterRef("name"))),
                is_in_shopping_cart=Exists(
                    shoping_cart.filter(name=OuterRef("name"))
                ),
            )
        return queryset

    @action(
        methods=("get",),
        detail=False,
        permission_classes=(drf_permission.IsAuthenticated,),
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        return FileResponse(
            get_pdf(self.request.user),
            as_attachment=True,
            filename="shopping-list.pdf",
        )

    def get_serializer_class(self):
        if self.action in (
            "update",
            "create",
            "partial_update",
        ):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer


class BaseFavoriteRecipeShopingCartViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = (drf_permission.IsAuthenticated,)
    serializer_class = FavoriteRecipeSerializer

    def create(self, request, *args, **kwargs):
        id = kwargs.pop("id")
        recipe = Recipe.objects.get(id=id)
        getattr(request.user, self.attribute).add(recipe)
        serializer = FavoriteRecipeSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["delete"], detail=False)
    def delete(self, request, *args, **kwargs):
        id = kwargs.pop("id")
        recipe = Recipe.objects.get(id=id)
        getattr(request.user, self.attribute).remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(BaseFavoriteRecipeShopingCartViewSet):
    attribute = "favorites"


class ShoppingCartViewSet(BaseFavoriteRecipeShopingCartViewSet):
    attribute = "shopping_cart"


class SubscriptionsViewSet(viewsets.ModelViewSet):
    permission_classes = (drf_permission.IsAuthenticated,)
    pagination_class = Pagination
    serializer_class = SubscriptionsSerializer

    @action(detail=True)
    def subscribe(self, request, id):
        subscribed = User.objects.get(id=id)
        request.user.subscriptions.add(subscribed)
        subscribed.is_subscribed = True
        serializer = SubscriptionsSerializer(subscribed)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True)
    def unsubscribe(self, request, id):
        subscribed = User.objects.get(id=id)
        request.user.subscriptions.remove(subscribed)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(subscriptions__id=user.id).annotate(
            recipes_count=Count("recipes"),
            is_subscribed=Exists(
                user.subscriptions.through.objects.filter(
                    from_user_id=OuterRef("id"),
                )
            ),
        )
        return queryset
