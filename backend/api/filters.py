from django_filters import rest_framework as filters
from recipes.models import Recipe


class RecipeFilterSet(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name="tags__slug")
    is_favorited = filters.BooleanFilter(method="get_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(method="get_is_in_shopping_cart")

    # def get_tags(self, queryset, name, value):
    #     print(name,value)
    #     return name

    def get_is_in_shopping_cart(self, queryset, name, value):
        return queryset.filter(is_in_shopping_cart=True) if value else queryset

    def get_is_favorited(self, queryset, name, value):
        return queryset.filter(is_favorited=True) if value else queryset

    class Meta:
        model = Recipe
        fields = ("author",)
