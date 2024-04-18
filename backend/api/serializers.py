from django.contrib.auth import get_user_model
from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import exceptions, fields, relations, serializers, status
from rest_framework.validators import UniqueTogetherValidator
from recipes import models
from recipes.fields import Base64ImageField
from users.models import Subscribe

User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password', 'id'
        )


class UserSerializer(BaseUserSerializer):
    is_subscribed = fields.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        read_only_fields = (
            'email',
            'id',
            'first_name',
            'last_name',
            'username'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=user,
            following=obj
        ).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=models.Tag.objects.all(),
                fields=('name', 'color', 'slug')
            )
        ]


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ingredient
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=models.Ingredient.objects.all(),
                fields=('name', 'measurement_unit')
            )
        ]


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    id = fields.IntegerField(write_only=True)
    amount = fields.IntegerField(write_only=True)

    class Meta:
        model = models.IngredientToRecipe
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = fields.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = fields.SerializerMethodField(read_only=True)
    is_in_shopping_cart = fields.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Recipe
        fields = (
            'id', 'author', 'tags',
            'ingredients', 'image',
            'name', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart',
            'text'
        )

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredienttorecipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shopping_carts.filter(recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientToRecipeSerializer(
        many=True,
        required=True,
        allow_empty=False,
        allow_null=False
    )
    image = Base64ImageField()
    tags = relations.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Tag.objects.all(),
        required=True,
        allow_empty=False,
        allow_null=False
    )

    class Meta:
        model = models.Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time',
                  'author')
        validators = [
            UniqueTogetherValidator(
                queryset=models.Recipe.objects.all(),
                fields=('author', 'name')
            )
        ]

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = models.Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            ingredient_data = get_object_or_404(
                models.Ingredient,
                id=ingredient['id']
            )
            models.IngredientToRecipe.objects.get_or_create(
                ingredient=ingredient_data,
                amount=ingredient['amount'],
                recipe=recipe
            )
        for tag in tags:
            current_tag = get_object_or_404(models.Tag, id=tag.id)
            models.TagToRecipe.objects.create(
                tag=current_tag, recipe=recipe
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        if 'ingredients' not in validated_data or 'tags' not in validated_data:
            raise exceptions.ValidationError(
                'Необходимо добавить ингредиенты/теги.',
                code=status.HTTP_400_BAD_REQUEST
            )
        else:
            tags = validated_data.pop('tags')
            ingredients = validated_data.pop('ingredients')
            instance.tags.clear()
            instance.tags.set(tags)
            instance.ingredients.clear()
        # updated_ingredients = []
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                models.Ingredient,
                id=ingredient['id']
            )
            models.IngredientToRecipe.objects.create(
                recipe=instance,
                amount=ingredient['amount'],
                ingredient=current_ingredient
            )
        #     updated_ingredients.append(current_ingredient)
        # instance.ingredients.set(updated_ingredients)
        instance.save()
        return instance

    def validate_tags(self, value):
        tags = value
        used_tags = []
        for tag in tags:
            if tag in used_tags:
                raise serializers.ValidationError(
                    'Теги не должны повторяться для одного рецепта.'
                )
            used_tags.append(tag)
        return value

    def validate_ingredients(self, value):
        ingredients = value
        used_ingredients = []
        for ingredient in ingredients:
            if not models.Ingredient.objects.filter(
                id=ingredient['id']
            ).exists():
                raise serializers.ValidationError(
                    'Ингредиент не существует.',
                    code=status.HTTP_400_BAD_REQUEST
                )
            elif ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть меньше одного.',
                    code=status.HTTP_400_BAD_REQUEST
                )
            else:
                if ingredient['id'] in used_ingredients:
                    raise serializers.ValidationError(
                        'Ингредиент в рецепте не может '
                        'быть представлен более 1 раза.'
                    )
                used_ingredients.append(ingredient['id'])
        return value

    def to_representation(self, instance):
        request = self.context['request']
        serializer = RecipeReadSerializer(
            instance,
            context={
                'request': request
            }
        )
        return serializer.data


class StandartRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(UserSerializer):
    recipes = fields.SerializerMethodField(read_only=True)
    recipes_count = fields.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count')
        read_only_fields = ('email', 'username',
                            'first_name', 'last_name')

    def validate(self, data):
        user = self.context['request'].user
        following = self.instance
        if user == following:
            raise exceptions.ValidationError(
                'Нельзя подписаться на самого себя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        if Subscribe.objects.filter(
            user=user,
            following=following
        ).exists():
            raise exceptions.ValidationError(
                'Нельзя подписаться повторно на того же '
                'пользователя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = StandartRecipeSerializer(
            recipes, many=True, read_only=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
