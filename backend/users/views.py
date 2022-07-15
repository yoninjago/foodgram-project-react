from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.pagination import LimitPageNumberPagination
from .models import Follow, User
from .serializers import CustomUserSerializer, FollowSerializer

SUBSCRIPTION_EXIST = 'Подписка уже существует'
SUBSCRIPTION_NOT_EXIST = 'Подписка на данного пользователя отсутствует'
SELF_SUBSCRIPTION = 'Подписка на себя запрещена!'


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

    def post(self, request, id):
        if id == request.user.id:
            return Response(
                {'error': SELF_SUBSCRIPTION},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(user=request.user, author_id=id).exists():
            return Response(
                {'error': SUBSCRIPTION_EXIST},
                status=status.HTTP_400_BAD_REQUEST
            )
        author = get_object_or_404(User, id=id)
        Follow.objects.create(user=request.user, author_id=id)
        return Response(
            FollowSerializer(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, id):
        get_object_or_404(User, id=id)
        subscription = Follow.objects.filter(user=request.user, author_id=id)
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': SUBSCRIPTION_NOT_EXIST},
            status=status.HTTP_400_BAD_REQUEST
        )
