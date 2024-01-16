from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from users.models import Subscription
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)

from .filters import CustomSearchFilter, RecipeFilterSet
from .paginations import PageLimitPagination
from .permissions import AuthorOrReadOnlyPermission
from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          NewAccountSerializer, RecipeDetailSerializer,
                          RecipeWriteSerializer, ShoppingCartRecipeSerializer,
                          SubscriptionInfoSerializer, TagSerializer,
                          UserDataSerializer)

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (CustomSearchFilter,)
    search_fields = ('name',)


class NewUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = NewAccountSerializer
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return UserDataSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if user == author:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            subscription = Subscription.objects.create(
                user=user,
                author=author
            )
            serializer = SubscriptionInfoSerializer(
                subscription,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        the_subscribe = get_object_or_404(
            Subscription,
            user=user,
            author=author
        )
        the_subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def subscriptions(self, request):
        user = request.user
        queryset = Subscription.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionInfoSerializer(
            pages,
            context={
                'request': request,
            },
            many=True,
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    permission_classes = [AuthorOrReadOnlyPermission]
    filterset_class = RecipeFilterSet
    pagination_class = PageLimitPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeDetailSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE']
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            data = {'user': request.user.id, 'recipe': pk}
            serializer = FavoriteRecipeSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            model_instance = Favorite.objects.filter(
                user=request.user.id, recipe__id=pk
            )
            if model_instance.exists():
                model_instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['POST', 'DELETE']
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            data = {'user': request.user.id, 'recipe': pk}
            serializer = ShoppingCartRecipeSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            model_instance = ShoppingCart.objects.filter(
                user=request.user.id, recipe__id=pk
            )
            if model_instance.exists():
                model_instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['GET']
    )
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientInRecipe.objects.filter(
                recipe__cart__user=request.user)
            .order_by('ingredient__name')
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(ingredient_value=Sum('amount')))

        if not ingredients:
            return Response(status=status.HTTP_204_NO_CONTENT)

        shopping_list = (
            f'Foodgram user {request.user} - shopping list\n\n'
        )

        for ingredient in ingredients:
            item = (
                f'• {ingredient["ingredient__name"]} - '
                f'{ingredient["ingredient_value"]} '
                f'{ingredient["ingredient__measurement_unit"]}'
            )
            shopping_list += item + '\n'

        filename = 'foodgram_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
