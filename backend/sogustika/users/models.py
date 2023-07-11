from django.db import models

from django.contrib.auth.models import AbstractUser


class AppUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Адрес электронной почты',)
    first_name = models.CharField(max_length=50, blank=False, verbose_name='Имя',)
    last_name = models.CharField(max_length=50, blank=False, verbose_name='фамилия',)
    REQUIRED_FIELDS = ('email', 'first_name', 'last_name',)
