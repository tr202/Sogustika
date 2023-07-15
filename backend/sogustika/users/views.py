from typing import Any
from django.db.models import Exists, Value, OuterRef, Subquery, Count
from rest_framework.decorators import action
from rest_framework import filters, viewsets, status
from rest_framework import permissions as drf_permission
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from djoser.views import UserViewSet

from recipes.models import Recipe
from users.models import AppUser, FavoriteUser
from users.serializers import AppUserSerializer , SubscriptionsSerializer


class UsersPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'limit'
    max_page_size = 100


def construct_queryset(self):
    favorite_users_queryset = FavoriteUser.objects.filter(user=OuterRef('pk'), subscriber = self.request.user)
    users_queryset = AppUser.objects.annotate(is_subscribed=Exists(favorite_users_queryset)).filter(is_subscribed=True)
    users_queryset =  users_queryset .annotate(recipes_count=Count('recipes'))
    return users_queryset

class AppUserViewSet(UserViewSet):
    pagination_class = UsersPagination
    permission_classes = (drf_permission.IsAuthenticated, )
    serializer_class = AppUserSerializer
    def dispatch(self, request, *args, **kwargs):
        self.pk = kwargs.get('id')
        return super().dispatch(request, *args, **kwargs)
    def get_queryset(self):
        if self.request.user.is_authenticated:
            favorite_users_queryset = FavoriteUser.objects.filter(user=OuterRef('pk'), subscriber = self.request.user)
            users_queryset = AppUser.objects.annotate(is_subscribed=Exists(favorite_users_queryset))
        elif self.pk:
            users_queryset = AppUser.objects.filter(pk=self.pk).annotate(is_subscribed = Value(False))
        return users_queryset
    
    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes =  (drf_permission.AllowAny, )
        return super().get_permissions()
    
  
class SubscriptionsViewSet(viewsets.ModelViewSet):
    permission_classes = (drf_permission.IsAuthenticated,)
    pagination_class = UsersPagination
    serializer_class = SubscriptionsSerializer
    def get_queryset(self):
        return construct_queryset(self)
    
        

class SubscribeViewSet(viewsets.ModelViewSet):
    lookup_fields = ('id',)
    permission_classes = (drf_permission.IsAuthenticated,)
    
     
    def create(self, request, *args, **kwargs):
        subscriber_id = request.user.pk
        id = kwargs.pop('id')
        user = AppUser.objects.filter(id=id)
        FavoriteUser.objects.create(user_id = id, subscriber_id = subscriber_id)
        favorite = FavoriteUser.objects.filter(user_id=id, subscriber_id=subscriber_id)
        user = user.annotate(is_subscribed=Exists(favorite)).get(id=id)
        serializer = AppUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED,)
    
    
    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        user_id = kwargs.pop('id') 
        subscriber_id = request.user.pk
        FavoriteUser.objects.filter(user_id = user_id, subscriber_id = subscriber_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    