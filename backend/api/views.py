from os import path

from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from foodgram.settings import BASE_DIR
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow, User
from .filters import RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          FollowSerializer, MinimumRecipeSerializer,
                          RecipeGetSerializer, RecipeSerializer, TagSerializer)


RECIPE_IN_LIST = 'Рецепт уже добавлен в список'
RECIPE_NOT_IN_LIST = 'Данного рецепта нет в списке'
DOCUMENT_TITLE = 'Foodgram, «Продуктовый помощник»'
FONT_NAME = 'lobster'
FONT_PATH = path.join(BASE_DIR, f'data/{FONT_NAME}.ttf')
SHOPPING_CART_TEMPLATE = '• {} ({}) - {}'
SUBSCRIPTION_EXIST = 'Подписка уже существует'
SUBSCRIPTION_NOT_EXIST = 'Подписка на данного пользователя отсутствует'
SELF_SUBSCRIPTION = 'Подписка на себя запрещена!'


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeSerializer

    @staticmethod
    def post_method(model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': RECIPE_IN_LIST},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        return Response(
            MinimumRecipeSerializer(recipe).data,
            status=status.HTTP_201_CREATED
            )

    @staticmethod
    def delete_method(request, pk, model):
        obj = model.objects.filter(user=request.user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': RECIPE_NOT_IN_LIST},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=["POST"])
    def favorite(self, request, pk):
        return self.post_method(Favorite, pk=pk, user=request.user)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method(
            request=request, pk=pk, model=Favorite)

    @action(detail=True, methods=["POST"])
    def shopping_cart(self, request, pk):
        return self.post_method(ShoppingCart, pk=pk, user=request.user)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method(
            request=request, pk=pk, model=ShoppingCart)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        shopping_cart = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user).values_list(
                    'ingredient__name',
                    'ingredient__measurement_unit'
                ).annotate(amount=Sum('amount'))
        pdfmetrics.registerFont(
            TTFont(FONT_NAME, FONT_PATH, 'UTF-8')
            )
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment;''filename="shopping_cart.pdf"'
            )
        pdf_doc = canvas.Canvas(response)
        pdf_doc.setTitle(DOCUMENT_TITLE)
        pdf_doc.setFont(FONT_NAME, size=32)
        pdf_doc.drawCentredString(300, 800, 'Список покупок')
        pdf_doc.line(100, 780, 480, 780)
        pdf_doc.setFont(FONT_NAME, size=18)
        height = 750
        for ingredient in shopping_cart:
            pdf_doc.drawString(
                75, height, (SHOPPING_CART_TEMPLATE.format(*ingredient))
            )
            height -= 25
        pdf_doc.showPage()
        pdf_doc.save()
        return response


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitPageNumberPagination


class FollowListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowSerializer
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class FollowViewSet(APIView):
    """
    Добавляет и удаляет подписки на автора.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        if pk == request.user.id:
            return Response(
                {'error': SELF_SUBSCRIPTION},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(user=request.user, author_id=pk).exists():
            return Response(
                {'error': SUBSCRIPTION_EXIST},
                status=status.HTTP_400_BAD_REQUEST
            )
        author = get_object_or_404(User, pk=pk)
        Follow.objects.create(user=request.user, author_id=pk)
        return Response(
            FollowSerializer(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        get_object_or_404(User, id=pk)
        subscription = Follow.objects.filter(user=request.user, author_id=pk)
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': SUBSCRIPTION_NOT_EXIST},
            status=status.HTTP_400_BAD_REQUEST
        )
