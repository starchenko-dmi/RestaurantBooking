from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя"""

    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True, null=True)

    avatar = models.ImageField(upload_to="avatars/", verbose_name="Аватар", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.username} ({self.email})"
