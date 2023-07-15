#from cats.views import AchievementViewSet, CatViewSet
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    #path('api/', include('djoser.urls')),  # Работа с пользователями
    #path('api/auth/', include('djoser.urls.authtoken')),  # Работа с токенами
]