from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'all_tags', 'get_favorite_count')
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('get_favorite_count',)

    def get_favorite_count(self, obj):
        return obj.favorites.count()

    get_favorite_count.short_description = 'Кол-во добавлений в избранное'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
