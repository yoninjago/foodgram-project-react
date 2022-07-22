from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CustomUserViewSet, FollowListView, FollowViewSet,
                    IngredientsViewSet, RecipesViewSet, TagsViewSet)

router = SimpleRouter()

router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('users', CustomUserViewSet, basename='users')


urlpatterns = [
    path(
        'users/subscriptions/',
        FollowListView.as_view(),
        name='subscriptions'
    ),
    path(
        'users/<int:pk>/subscribe/',
        FollowViewSet.as_view(),
        name='subscribe'
    ),
    path('', include(router.urls)),
    url('', include('djoser.urls')),
    url('auth/', include('djoser.urls.authtoken')),
]
