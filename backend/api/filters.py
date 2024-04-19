from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag
from .constants import FALSE_FILTER_VALUE, TRUE_FILTER_VALUE


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value == TRUE_FILTER_VALUE and not user.is_anonymous:
            return queryset.filter(favorites__user=user)
        elif value == FALSE_FILTER_VALUE and not user.is_anonymous:
            excluded_favorited = (
                recipe.name for recipe in queryset.filter(
                    favorites__user=user)
            )
            return queryset.exclude(name__in=excluded_favorited)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value == TRUE_FILTER_VALUE and not user.is_anonymous:
            return queryset.filter(shopping_carts__user=user)
        elif value == FALSE_FILTER_VALUE and not user.is_anonymous:
            excluded_shopping_cart = (
                recipe.name for recipe in queryset.filter(
                    shopping_carts__user=user)
            )
            return queryset.exclude(name__in=excluded_shopping_cart)
        return queryset
