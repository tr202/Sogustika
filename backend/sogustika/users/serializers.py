from django.contrib.auth import authenticate

from rest_framework import serializers

from djoser.conf import settings

from users.models import AppUser

from djoser.serializers import TokenCreateSerializer, UserSerializer

User = AppUser

class AppUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = settings.DEFAULT_USER_SERIALIZER_FIELDS
        read_only_fields = (settings.LOGIN_FIELD,)



class AppTokenCreateSerializer(TokenCreateSerializer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.fields[settings.APP_LOGIN_FIELD] = serializers.CharField(required=False)

    def validate(self, attrs):
        password = attrs.get("password")
        params = {settings.APP_LOGIN_FIELD: attrs.get(settings.APP_LOGIN_FIELD)}
        self.user = authenticate(
            request=self.context.get("request"), **params, password=password
        )
        if not self.user:
            self.user = User.objects.filter(**params).first()
            if self.user and not self.user.check_password(password):
                self.fail("invalid_credentials")
        if self.user and self.user.is_active:
            return attrs
        self.fail("invalid_credentials")
