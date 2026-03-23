from datetime import datetime, time, timedelta

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from .validators import validate_image_dimensions, validate_image_file_size


class SiteContent(models.Model):
    """Контент сайта (история, миссия и т.д.)"""

    CONTENT_TYPE_CHOICES = [
        ("about_history", "История ресторана"),
        ("about_mission", "Миссия"),
        ("home_title", "Заголовок главной"),
        ("home_description", "Описание главной"),
        ("contacts_title", "Заголовок контактов"),
    ]

    key = models.CharField(max_length=50, unique=True, choices=CONTENT_TYPE_CHOICES, verbose_name="Ключ")
    title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержимое")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Элемент контента"
        verbose_name_plural = "Элементы контента"
        ordering = ["key"]

    def __str__(self):
        return f"{self.get_key_display()}"

    def get_value(self):
        """Возвращает значение контента"""
        return self.content


class TeamMember(models.Model):
    """Модель для команды ресторана (страница "О нас")"""

    POSITION_CHOICES = [
        ("chef", "Шеф-повар"),
        ("cook", "Повар"),
        ("manager", "Менеджер"),
        ("waiter", "Официант"),
        ("bartender", "Бармен"),
        ("other", "Другое"),
    ]

    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default="other", verbose_name="Должность")
    photo = models.ImageField(upload_to="team/", verbose_name="Фото")
    bio = models.TextField(blank=True, verbose_name="О себе")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")

    class Meta:
        verbose_name = "Член команды"
        verbose_name_plural = "Команда ресторана"
        ordering = ["order", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_position_display()})"


class Service(models.Model):
    """Модель для услуг ресторана (главная страница)"""

    title = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(verbose_name="Описание")
    icon = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Иконка (Bootstrap icon class)",
        help_text="Например: bi-star, bi-heart",
    )
    image = models.ImageField(upload_to="services/", blank=True, null=True, verbose_name="Изображение")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги ресторана"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title


class RestaurantSettings(models.Model):
    """Настройки ресторана (время работы, параметры бронирования)"""

    name = models.CharField(max_length=200, default="Настройки", verbose_name="Название")
    opening_time = models.TimeField(default=time(10, 0), verbose_name="Время открытия")
    closing_time = models.TimeField(default=time(23, 0), verbose_name="Время закрытия")
    closes_next_day = models.BooleanField(
        default=False,
        verbose_name="Закрывается на следующий день",
        help_text="Отметьте, если ресторан работает после полуночи",
    )
    min_booking_duration = models.PositiveSmallIntegerField(
        default=1, verbose_name="Мин. длительность бронирования (часов)"
    )
    max_booking_duration = models.PositiveSmallIntegerField(
        default=5, verbose_name="Макс. длительность бронирования (часов)"
    )
    min_advance_booking = models.PositiveSmallIntegerField(default=0, verbose_name="Мин. время до бронирования (часов)")
    max_advance_booking = models.PositiveSmallIntegerField(
        default=60, verbose_name="Макс. время до бронирования (дней)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активны")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    address = models.CharField(max_length=500, blank=True, verbose_name="Адрес ресторана")
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Широта (latitude)"
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Долгота (longitude)"
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email")

    class Meta:
        verbose_name = "Настройки ресторана"
        verbose_name_plural = "Настройки ресторана"

    def __str__(self):
        next_day = " (+1)" if self.closes_next_day else ""
        return f"{self.name} ({self.opening_time} - {self.closing_time}{next_day})"

    def save(self, *args, **kwargs):
        if not self.pk and RestaurantSettings.objects.exists():
            raise ValidationError("Может быть только одна запись настроек")
        return super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Получить настройки (создаёт если нет)"""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                "name": "Основные настройки",
                "opening_time": time(10, 0),
                "closing_time": time(23, 0),
                "closes_next_day": False,
                "min_booking_duration": 1,
                "max_booking_duration": 5,
            },
        )
        return settings

    def get_closing_datetime(self, date):
        """Получить datetime закрытия для данной даты"""
        closing_datetime = datetime.combine(date, self.closing_time)

        if self.closes_next_day:
            closing_datetime += timedelta(days=1)

        return closing_datetime


class SocialLink(models.Model):
    """Ссылки на социальные сети"""

    # Выбор соцсети с предустановленными иконками
    SOCIAL_NETWORK_CHOICES = [
        ("telegram", "Telegram"),
        ("whatsapp", "WhatsApp"),
        ("vk", "ВКонтакте"),
        ("odnoklassniki", "Одноклассники"),
        ("youtube", "YouTube"),
        ("rutube", "Rutube"),
        ("zen", "Яндекс.Дзен"),
        ("instagram", "Instagram"),
        ("facebook", "Facebook"),
        ("tiktok", "TikTok"),
        ("custom", "Другая соцсеть"),
    ]

    # Соответствие соцсетей иконкам Bootstrap
    ICON_MAP = {
        "telegram": "bi bi-telegram",
        "whatsapp": "bi bi-whatsapp",
        "vk": "bi bi-vk",
        "odnoklassniki": "bi bi-circle-fill",  # оранжевый круг
        "youtube": "bi bi-youtube",
        "rutube": "bi bi-play-circle",
        "zen": "bi bi-pen",
        "instagram": "bi bi-instagram",
        "facebook": "bi bi-facebook",
        "tiktok": "bi bi-music-note-beamed",
        "custom": "bi bi-share",
    }

    network = models.CharField(
        max_length=30, choices=SOCIAL_NETWORK_CHOICES, default="telegram", verbose_name="Социальная сеть"
    )
    url = models.URLField(verbose_name="Ссылка")
    custom_name = models.CharField(
        max_length=50, blank=True, help_text='Заполните, если выбрали "Другая соцсеть"', verbose_name="Название"
    )
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок сортировки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Ссылка на соцсеть"
        verbose_name_plural = "Ссылки на соцсети"
        ordering = ["order", "network"]

    def __str__(self):
        name = self.custom_name or self.get_network_display()
        return f"{name} - {self.url}"

    @property
    def icon_class(self):
        """Возвращает класс иконки для выбранной соцсети"""
        return self.ICON_MAP.get(self.network, "bi bi-share")

    @property
    def display_name(self):
        """Возвращает отображаемое название"""
        return self.custom_name if self.network == "custom" else self.get_network_display()

    def clean(self):
        # Проверка на количество активных ссылок (макс 5)
        if self.is_active:
            active_count = SocialLink.objects.filter(is_active=True).exclude(pk=self.pk).count()
            if active_count >= 5:
                raise ValidationError("Можно добавить не более 5 активных ссылок на соцсети.")

        # Если выбрана custom сеть, нужно указать название
        if self.network == "custom" and not self.custom_name:
            raise ValidationError("Укажите название для пользовательской соцсети.")


class FooterDocument(models.Model):
    """Документы в подвале (оферта, политика и т.д.)"""

    DOC_TYPE_CHOICES = [
        ("text", "Текстовый документ"),
        ("pdf", "PDF файл"),
    ]

    title = models.CharField(max_length=200, verbose_name="Название документа")
    slug = models.SlugField(
        unique=True,
        verbose_name="Слаг (для URL)",
        help_text="Латинские буквы, цифры и дефис (например: offer, privacy-policy)",
    )
    doc_type = models.CharField(max_length=10, choices=DOC_TYPE_CHOICES, default="text", verbose_name="Тип документа")
    content = models.TextField(
        blank=True, help_text="Заполните для текстового документа", verbose_name="Текст документа"
    )
    file = models.FileField(
        upload_to="documents/",
        blank=True,
        null=True,
        help_text="Загрузите PDF файл (макс. 5MB). Оставьте пустым, если используете текст.",
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf"]),
        ],
        verbose_name="PDF файл",
    )
    is_active = models.BooleanField(default=True, verbose_name="Опубликован")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Документ в подвале"
        verbose_name_plural = "Документы в подвале"
        ordering = ["title"]

    def __str__(self):
        return self.title

    def clean(self):
        # Проверка на количество активных документов (макс 5)
        if self.is_active:
            active_count = FooterDocument.objects.filter(is_active=True).exclude(pk=self.pk).count()
            if active_count >= 5:
                raise ValidationError("Можно добавить не более 5 активных документов.")

        # Проверка: должен быть заполнен хотя бы один тип контента
        if not self.content and not self.file:
            raise ValidationError("Заполните текст документа или загрузите PDF файл.")

        # Проверка размера файла
        if self.file:
            max_size = 5 * 1024 * 1024  # 5MB
            if self.file.size > max_size:
                raise ValidationError(
                    f"Размер файла не должен превышать 5MB. Ваш файл: {self.file.size / 1024 / 1024:.2f}MB"
                )


class HeroImage(models.Model):
    """Изображение для hero секции на главной"""

    key = models.CharField(max_length=50, unique=True, default="home_hero", editable=False, verbose_name="Ключ")
    image = models.ImageField(
        upload_to="hero_images/",
        verbose_name="Изображение",
        help_text="📐 Рекомендуемый размер: 1920×800px<br>"
        "⚖️ Максимальный размер: 2MB<br>"
        "📁 Форматы: JPG, PNG, WEBP<br>"
        "💡 Совет: используйте фото интерьера с тёплым освещением",
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            validate_image_file_size,
        ],
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Изображение главного баннера"
        verbose_name_plural = "Изображения главных баннеров"

    def __str__(self):
        return f"Баннер: {self.key}"

    def clean(self):
        if self.image:
            # Проверка размеров
            try:
                validate_image_dimensions(self.image, min_width=1600, min_height=600)
            except ValidationError as e:
                raise e
