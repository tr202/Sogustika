from rest_framework import permissions as drf_permission
from djoser.views import UserViewSet


class AppUserViewSet(UserViewSet):
    permission_classes = (drf_permission.AllowAny, )
    
