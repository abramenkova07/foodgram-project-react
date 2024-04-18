from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from . import constants

User = get_user_model()


class NameBaseModel(models.Model):
    name = models.CharField(
        'Название',
        max_length=constants.NAME_LENGTH
    )

    class Meta:
        abstract = True


class Tag(NameBaseModel):
    color = models.CharField(
        'Цвет',
        max_length=constants.COLOR_LENGTH, unique=True,
        help_text='Цвет должен быть представлен '
                  'в формате HEX (например, #ff0000).',
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Код цвета не соответствует формату HEX.')
        ]
    )
    slug = models.SlugField(
        'Слаг',
        max_length=constants.SLUG_LENGTH, unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'slug', 'color'],
                name='unique_name_slug_color'
            )
        ]

    def __str__(self):
        return self.name[:constants.MAX_SHOWING_LENGTH]


class Ingredient(NameBaseModel):
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=constants.MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return self.name[:constants.MAX_SHOWING_LENGTH]


class Recipe(NameBaseModel):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientToRecipe',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagToRecipe',
        verbose_name='Теги'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        verbose_name='Изображение рецепта'
    )
    text = models.TextField(
        'Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (мин)'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique_author_name'
            )
        ]
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self):
        return self.name[:constants.MAX_SHOWING_LENGTH]

    @admin.display(description='Теги')
    def all_tags(self):
        return ', '.join([tag.name for tag in self.tags.all()])


class RecipeBaseModel(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True


class IngredientToRecipe(RecipeBaseModel):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ('ingredient',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return (f'{self.ingredient.name[:constants.MAX_SHOWING_LENGTH]} - '
                f'{self.recipe.name[:constants.MAX_SHOWING_LENGTH]}')


class TagToRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Тег'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('tag',)
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return (f'{self.tag.name[:constants.MAX_SHOWING_LENGTH]} - '
                f'{self.recipe.name[:constants.MAX_SHOWING_LENGTH]}')


class UserBaseModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    class Meta:
        abstract = True


class Favorite(RecipeBaseModel, UserBaseModel):
    pass

    class Meta:
        ordering = ('user',)
        verbose_name = 'любимый рецепт'
        verbose_name_plural = 'любимые рецепты'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_favorite'
            )
        ]

    def __str__(self):
        return (f'{self.user.username[:constants.MAX_SHOWING_LENGTH]} - '
                f'{self.recipe.name[:constants.MAX_SHOWING_LENGTH]}')


class ShoppingCart(RecipeBaseModel, UserBaseModel):
    pass

    class Meta:
        ordering = ('user',)
        verbose_name = 'рецепт в корзине покупок'
        verbose_name_plural = 'рецепты в корзине покупок'
        default_related_name = 'shopping_carts'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_shopping_cart'
            )
        ]

    def __str__(self):
        return (f'{self.user.username[:constants.MAX_SHOWING_LENGTH]} - '
                f'{self.recipe.name[:constants.MAX_SHOWING_LENGTH]}')
