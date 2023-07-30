from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework.authtoken.models import TokenProxy

from users.models import Subscribtion

User = get_user_model()

if not settings.DEBUG:
    admin.site.unregister(TokenProxy)
    admin.site.unregister(Group)

admin.site.register(Subscribtion)


@admin.register(User)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'first_name',
                    'last_name',
                    'username',
                    'email',
                    'is_superuser',)
    list_filter = ('first_name', 'email',)
