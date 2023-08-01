from django.contrib.auth.models import AbstractUser
from django.db import models
from recipes.models import Recipe


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name="Адрес электронной почты",
    )
    first_name = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="фамилия",
    )
    favorites = models.ManyToManyField(
        Recipe, blank=True, default=False, related_name="favorite_recipe"
    )
    subscriptions = models.ManyToManyField(
        "self", blank=True, default=False, related_name="subscriptions"
    )
    shopping_cart = models.ManyToManyField(
        Recipe, blank=True, default=False, related_name="shopping_cart"
    )

    def __str__(self):
        return self.username
