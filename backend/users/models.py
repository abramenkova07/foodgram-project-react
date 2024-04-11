from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import EMAIL_LENGHT, NAME_LENGTH


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=EMAIL_LENGHT,
        unique=True,
        blank=False
    )
    first_name = models.CharField(
        'Имя',
        max_length=NAME_LENGTH,
        blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=NAME_LENGTH,
        blank=False
    )


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Кто подписан',
        related_name='followers')
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='На кого подписан',
        related_name='followings')

    class Meta:
        ordering = ('following',)
        verbose_name = 'подписывание'
        verbose_name_plural = 'подписывания'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]

    def __str__(self):
        return (f'{self.user} подписан на {self.following}')
