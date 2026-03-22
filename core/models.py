from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from datetime import time, datetime, timedelta


class SiteContent(models.Model):
    """Контент сайта (история, миссия и т.д.)"""

    CONTENT_TYPE_CHOICES = [
        ('about_history', 'История ресторана'),
        ('about_mission', 'Миссия'),
        ('home_title', 'Заголовок главной'),
        ('home_description', 'Описание главной'),
        ('contacts_title', 'Заголовок контактов'),
    ]

    key = models.CharField(
        max_length=50,
        unique=True,
        choices=CONTENT_TYPE_CHOICES,
        verbose_name='Ключ'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Заголовок'
    )
    content = models.TextField(
        verbose_name='Содержимое'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Элемент контента'
        verbose_name_plural = 'Элементы контента'
        ordering = ['key']

    def __str__(self):
        return f'{self.get_key_display()}'

    def get_value(self):
        """Возвращает значение контента"""
        return self.content


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


class RestaurantSettings(models.Model):
    """Настройки ресторана (время работы, параметры бронирования)"""

    name = models.CharField(
        max_length=200,
        default='Настройки',
        verbose_name='Название'
    )
    opening_time = models.TimeField(
        default=time(10, 0),
        verbose_name='Время открытия'
    )
    closing_time = models.TimeField(
        default=time(23, 0),
        verbose_name='Время закрытия'
    )
    closes_next_day = models.BooleanField(
        default=False,
        verbose_name='Закрывается на следующий день',
        help_text='Отметьте, если ресторан работает после полуночи'
    )
    min_booking_duration = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Мин. длительность бронирования (часов)'
    )
    max_booking_duration = models.PositiveSmallIntegerField(
        default=5,
        verbose_name='Макс. длительность бронирования (часов)'
    )
    min_advance_booking = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Мин. время до бронирования (часов)'
    )
    max_advance_booking = models.PositiveSmallIntegerField(
        default=60,
        verbose_name='Макс. время до бронирования (дней)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активны'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Адрес ресторана'
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Широта (latitude)'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Долгота (longitude)'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='Email'
    )

    class Meta:
        verbose_name = 'Настройки ресторана'
        verbose_name_plural = 'Настройки ресторана'

    def __str__(self):
        next_day = ' (+1)' if self.closes_next_day else ''
        return f'{self.name} ({self.opening_time} - {self.closing_time}{next_day})'

    def save(self, *args, **kwargs):
        if not self.pk and RestaurantSettings.objects.exists():
            raise ValidationError('Может быть только одна запись настроек')
        return super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Получить настройки (создаёт если нет)"""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'name': 'Основные настройки',
                'opening_time': time(10, 0),
                'closing_time': time(23, 0),
                'closes_next_day': False,
                'min_booking_duration': 1,
                'max_booking_duration': 5,
            }
        )
        return settings

    def get_closing_datetime(self, date):
        """Получить datetime закрытия для данной даты"""
        closing_datetime = datetime.combine(date, self.closing_time)

        if self.closes_next_day:
            closing_datetime += timedelta(days=1)

        return closing_datetime
