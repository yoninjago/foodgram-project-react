from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers

from .views import CustomUserViewSet, FollowListView, FollowViewSet

router = routers.SimpleRouter()

router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path(
        'users/subscriptions/',
        FollowListView.as_view(),
        name='subscriptions'
    ),
    path(
        'users/<int:id>/subscribe/',
        FollowViewSet.as_view(),
        name='subscribe'
    ),
    path('', include(router.urls)),
    url('', include('djoser.urls')),
    url('auth/', include('djoser.urls.authtoken')),
]
