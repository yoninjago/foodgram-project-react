from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import IngredientsViewSet, RecipesViewSet, TagsViewSet

router = SimpleRouter()

router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
]
