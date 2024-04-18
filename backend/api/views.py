from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes import models
from users.models import Subscribe

from . import serializers
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthenticatedOrAuthor

User = get_user_model()


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, **kwargs):
        user = request.user
        following = get_object_or_404(
            User,
            id=kwargs.get('id')
        )
        if request.method == 'POST':
            serializer = serializers.SubscribeSerializer(
                instance=following,
                data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            # Subscribe.objects.create(user=user, following=following)
            serializer.save(user=user, following=following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            subscription = Subscribe.objects.filter(
                user=user, following=following
            )
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(data={
                'errors': 'Невозможно удалить. '
                'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False,
            methods=['get'],
            serializer_class=serializers.SubscribeSerializer,
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request, **kwargs):
        user = request.user
        subscriptions = User.objects.filter(followings__user=user).order_by(
            'username')
        page = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(instance=page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            methods=['get'],
            serializer_class=serializers.UserSerializer,
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request, **kwargs):
        user_id = request.user.id
        chosen_user = get_object_or_404(User, id=user_id)
        serializer = self.get_serializer(
            chosen_user,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = models.Recipe.objects.prefetch_related(
        'ingredients', 'tags').select_related(
        'author')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAuthenticatedOrAuthor,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return serializers.RecipeReadSerializer
        return serializers.RecipeWriteSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        user = request.user
        if request.method == 'POST':
            return self.adding(
                request, pk, user, models.Favorite,
                serializers.StandartRecipeSerializer)
        return self.deleting(pk, user, models.Favorite)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        user = request.user
        if request.method == 'POST':
            return self.adding(
                request, pk, user, models.ShoppingCart,
                serializers.StandartRecipeSerializer)
        return self.deleting(pk, user, models.ShoppingCart)

    def adding(self, request, pk, user, model_name, serializer_name):
        if not models.Recipe.objects.select_related(
                'author').filter(id=pk).exists():
            return Response(
                data={
                    'errors': 'Такой рецепт не существует.'
                },
                status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(models.Recipe, id=pk)
        if model_name.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                data={
                    'errors': 'Нельзя повторно добавить рецепт.'
                },
                status=status.HTTP_400_BAD_REQUEST)
        serializer = serializer_name(
            instance=recipe,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        # model_name.objects.create(user=user, recipe=recipe)
        serializer.save(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def deleting(self, pk, user, model_name):
        recipe = get_object_or_404(models.Recipe, id=pk)
        data = model_name.objects.filter(
            user=user,
            recipe=recipe
        )
        if data.exists():
            data.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            data={
                'errors': 'Невозможно удалить. '
                          'Рецепт ранее не был вами добавлен.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False,
            methods=['get']
            )
    def download_shopping_cart(self, request):
        ingredients = models.IngredientToRecipe.objects.select_related(
            'ingredient', 'recipe').filter(
            recipe__shopping_carts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        current_date = timezone.now().date()
        shopping_cart = (f'Список покупок: {request.user.first_name} '
                         f'{request.user.last_name}, '
                         f'{current_date.strftime("%d.%m.%Y")} \n\n')
        for ingredient in ingredients:
            shopping_cart += (
                f'{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]}) '
                f'- {ingredient["ingredient_amount"]} \n'
            )
        shopping_cart += f'\nFoodgram {current_date.year}'
        filename = (f'{request.user.first_name}_{request.user.last_name}'
                    f'_shopping_cart.txt')
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
