from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


class Table(models.Model):
    """Модель столика в ресторане"""

    ZONE_CHOICES = [
        ('main', 'Основной зал'),
        ('vip', 'VIP-зона'),
        ('terrace', 'Терраса'),
        ('bar', 'Барная стойка'),
    ]

    number = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Номер столика'
    )
    capacity = models.PositiveSmallIntegerField(
        default=2,
        verbose_name='Вместимость (человек)'
    )
    zone = models.CharField(
        max_length=20,
        choices=ZONE_CHOICES,
        default='main',
        verbose_name='Зона'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )

    class Meta:
        verbose_name = 'Столик'
        verbose_name_plural = 'Столики'
        ordering = ['zone', 'number']

    def __str__(self):
        return f'Столик {self.number} ({self.get_zone_display()}, {self.capacity} чел.)'

    def is_available(self, date, time, duration=2):
        """
        Проверка доступности столика на указанное время

        Args:
            date: Дата бронирования
            time: Время начала
            duration: Длительность в часах (по умолчанию 2)

        Returns:
            bool: True если столик свободен
        """
        start_datetime = timezone.make_aware(timezone.datetime.combine(date, time))
        end_datetime = start_datetime + timedelta(hours=duration)

        # Ищем пересекающиеся бронирования
        overlapping_reservations = Reservation.objects.filter(
            table=self,
            status__in=['confirmed', 'pending'],
            date=date,
        ).filter(
            # Пересечение по времени
            models.Q(
                time__lt=end_datetime.time(),
                end_time__gt=start_datetime.time()
            )
        )

        return not overlapping_reservations.exists()

class Reservation(models.Model):
    """Модель бронирования столика"""

    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
        ('no_show', 'Клиент не пришёл'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Пользователь'
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Столик'
    )
    date = models.DateField(
        verbose_name='Дата бронирования'
    )
    time = models.TimeField(
        verbose_name='Время начала'
    )
    end_time = models.TimeField(
        verbose_name='Время окончания'
    )
    guests_count = models.PositiveSmallIntegerField(
        default=2,
        verbose_name='Количество гостей'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий клиента'
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
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['date', 'time']),
            models.Index(fields=['status']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f'Бронь {self.user.username} на {self.date} {self.time}'

    def clean(self):
        """Валидация бронирования"""
        # Проверяем только если столик выбран
        if hasattr(self, 'table') and self.table:
            if self.guests_count > self.table.capacity:
                raise ValidationError({
                    'guests_count': f'Количество гостей не может превышать вместимость столика ({self.table.capacity})'
                })

            if self.status in ['confirmed', 'pending']:
                # Проверяем доступность столика (исключая текущее бронирование)
                start_time = timezone.make_aware(timezone.datetime.combine(self.date, self.time))
                end_time = timezone.make_aware(timezone.datetime.combine(self.date, self.end_time))

                overlapping = Reservation.objects.filter(
                    table=self.table,
                    date=self.date,
                    status__in=['confirmed', 'pending'],
                ).exclude(
                    pk=self.pk  # Исключаем текущее бронирование при обновлении
                ).filter(
                    models.Q(
                        time__lt=self.end_time,
                        end_time__gt=self.time
                    )
                )

                if overlapping.exists():
                    raise ValidationError({
                        'time': 'Столик уже забронирован на это время'
                    })

    def save(self, *args, **kwargs):
        self.full_clean()  # Вызываем валидацию
        super().save(*args, **kwargs)

    def cancel(self):
        """Отмена бронирования"""
        self.status = 'cancelled'
        self.save()

    def confirm(self):
        """Подтверждение бронирования"""
        self.status = 'confirmed'
        self.save()

    def is_upcoming(self):
        """Проверка, является ли бронирование предстоящим"""
        now = timezone.now()
        reservation_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return reservation_datetime > now

    def can_cancel(self):
        """Можно ли отменить бронирование"""
        return self.status in ['pending', 'confirmed'] and self.is_upcoming()
