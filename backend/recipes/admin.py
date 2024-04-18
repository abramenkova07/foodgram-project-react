from django.contrib import admin

from recipes import models


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'all_tags', 'get_favorite_count')
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('get_favorite_count',)

    def get_favorite_count(self, obj):
        return obj.favorites.count()

    get_favorite_count.short_description = 'Кол-во добавлений в избранное'


@admin.register(models.IngredientToRecipe)
class IngredientToRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(models.ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
