from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.validators import ValidationError


class User(AbstractUser):
    email = models.EmailField(
        max_length=200,
        unique=True,
        verbose_name='E-mail',
    )
    username = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='User name',
    )
    first_name = models.CharField(
        max_length=200,
        verbose_name='First name'
    )
    last_name = models.CharField(
        max_length=200,
        verbose_name='Last name'
    )
    password = models.CharField(
        max_length=200,
        verbose_name='Password'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription_user',
        verbose_name='subscriber',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription_author',
        verbose_name='author',
    )

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription',
            )
        ]

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Cannot subscribe to yourself.')

    def __str__(self):
        return f'{self.user} is subscribed to {self.author}.'
