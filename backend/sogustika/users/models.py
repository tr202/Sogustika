from django.db import models

from django.contrib.auth.models import AbstractUser


class AppUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Адрес электронной почты',)
    first_name = models.CharField(max_length=50, blank=False, verbose_name='Имя',)
    last_name = models.CharField(max_length=50, blank=False, verbose_name='фамилия',)
    REQUIRED_FIELDS = ('email', 'first_name', 'last_name',)
    

class FavoriteUser(models.Model):
    subscriber = models.ForeignKey(AppUser,
                                   on_delete=models.CASCADE,
                                   related_name='subscriber')
    user = models.ForeignKey(AppUser,
                             on_delete=models.CASCADE,
                             related_name='has_subs',)
    
    
    class Meta:
        verbose_name_plural = 'любимые авторы'
        verbose_name = 'любимого автора'
        constraints = (
                models.UniqueConstraint(
                    name='no_double_favorite',
                    fields=('subscriber', 'user',)
                ),
            )
    ordering = ('user',)
    
    def __str__(self):
        return self.subscriber.username + ' подписан на ' + self.user.username
 