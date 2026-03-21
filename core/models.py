from django.db import models
from django.utils.text import slugify


class SiteContent(models.Model):
    """Модель для управления контентом сайта через админку"""

    CONTENT_TYPE_CHOICES = [
        ('text', 'Текст'),
        ('image', 'Изображение'),
        ('html', 'HTML'),
    ]

    key = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Ключ',
        help_text='Уникальный идентификатор (например: about_text, main_banner)'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Описание контента для админки'
    )
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='text',
        verbose_name='Тип контента'
    )
    text_value = models.TextField(
        blank=True,
        null=True,
        verbose_name='Текстовое значение'
    )
    image_value = models.ImageField(
        upload_to='content/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Элемент контента'
        verbose_name_plural = 'Контент сайта'
        ordering = ['title']

    def __str__(self):
        return f'{self.title} ({self.key})'

    def save(self, *args, **kwargs):
        """Автоматически создаём slug из title если key не заполнен"""
        if not self.key:
            self.key = slugify(self.title)
        super().save(*args, **kwargs)

    def get_value(self):
        """Возвращает значение в зависимости от типа контента"""
        if self.content_type == 'image':
            return self.image_value
        return self.text_value


class TeamMember(models.Model):
    """Модель для команды ресторана (страница "О нас")"""

    POSITION_CHOICES = [
        ('chef', 'Шеф-повар'),
        ('cook', 'Повар'),
        ('manager', 'Менеджер'),
        ('waiter', 'Официант'),
        ('bartender', 'Бармен'),
        ('other', 'Другое'),
    ]

    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия'
    )
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default='other',
        verbose_name='Должность'
    )
    photo = models.ImageField(
        upload_to='team/',
        verbose_name='Фото'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок отображения'
    )

    class Meta:
        verbose_name = 'Член команды'
        verbose_name_plural = 'Команда ресторана'
        ordering = ['order', 'last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.get_position_display()})'


class Service(models.Model):
    """Модель для услуг ресторана (главная страница)"""

    title = models.CharField(
        max_length=200,
        verbose_name='Название услуги'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    icon = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Иконка (Bootstrap icon class)',
        help_text='Например: bi-star, bi-heart'
    )
    image = models.ImageField(
        upload_to='services/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок отображения'
    )

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги ресторана'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title
