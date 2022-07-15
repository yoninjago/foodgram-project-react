from os import path

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


from foodgram.settings import BASE_DIR
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from .filters import RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, MinimumRecipeSerializer,
                          RecipeGetSerializer, RecipeSerializer, TagSerializer)

RECIPE_IN_LIST = 'Рецепт уже добавлен в список'
RECIPE_NOT_IN_LIST = 'Данного рецепта нет в списке'
DOCUMENT_TITLE = 'Foodgram, «Продуктовый помощник»'
FONT_NAME = 'lobster'
FONT_PATH = path.join(BASE_DIR, f'data/{FONT_NAME}.ttf')


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
        shopping_list = {}
        for ingredient in RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user).values_list(
                    'ingredient__name',
                    'ingredient__measurement_unit',
                    'amount'
                ):
            ingredient_name, measurement_unit, amount = ingredient
            if ingredient_name not in shopping_list:
                shopping_list[ingredient_name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                    }
            else:
                shopping_list[ingredient_name]['amount'] += amount
        pdfmetrics.registerFont(
            TTFont(FONT_NAME, FONT_PATH, 'UTF-8')
            )
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment;''filename="shopping_list.pdf"'
            )
        pdf_doc = canvas.Canvas(response)
        pdf_doc.setTitle(DOCUMENT_TITLE)
        pdf_doc.setFont(FONT_NAME, size=32)
        pdf_doc.drawCentredString(300, 800, 'Список покупок')
        pdf_doc.line(100, 780, 480, 780)
        pdf_doc.setFont(FONT_NAME, size=18)
        height = 750
        for ingredient_name, ingredient_data in shopping_list.items():
            pdf_doc.drawString(75, height, (
                f'• {ingredient_name} ({ingredient_data["measurement_unit"]}) '
                f'- {ingredient_data["amount"]} ')
            )
            height -= 25
        pdf_doc.showPage()
        pdf_doc.save()
        return response
