from django import forms
from django.contrib import admin
from django.utils.html import format_html, mark_safe

from .models import FooterDocument, HeroImage, RestaurantSettings, Service, SiteContent, SocialLink, TeamMember


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "is_active", "updated_at")
    list_filter = ("is_active", "key")
    search_fields = ("title", "content")
    list_editable = ("is_active",)

    fieldsets = (
        ("Основное", {"fields": ("key", "title", "content")}),
        ("Статус", {"fields": ("is_active",)}),
        ("Мета", {"fields": ("updated_at",), "classes": ("collapse",)}),
    )
    readonly_fields = ("updated_at",)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "position", "is_active", "order")
    list_filter = ("position", "is_active")
    search_fields = ("first_name", "last_name", "bio")
    list_editable = ("is_active", "order")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    list_editable = ("is_active", "order")


@admin.register(RestaurantSettings)
class RestaurantSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Основное", {"fields": ("name", "is_active")}),
        ("Контактная информация", {"fields": ("address", "phone", "email")}),
        (
            "Координаты для карты",
            {
                "fields": ("latitude", "longitude"),
                "description": "Укажите координаты ресторана (можно получить на maps.yandex.ru)",
            },
        ),
        ("Время работы", {"fields": ("opening_time", "closing_time", "closes_next_day")}),
        (
            "Параметры бронирования",
            {"fields": ("min_booking_duration", "max_booking_duration", "min_advance_booking", "max_advance_booking")},
        ),
        ("Мета", {"fields": ("updated_at",), "classes": ("collapse",)}),
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not RestaurantSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class SocialLinkAdminForm(forms.ModelForm):
    """Форма с подсказками для соцсетей"""

    class Meta:
        model = SocialLink
        fields = "__all__"
        widgets = {
            "network": forms.Select(attrs={"class": "form-control"}),
            "url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://..."}),
            "custom_name": forms.TextInput(attrs={"class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    form = SocialLinkAdminForm
    list_display = ("display_name", "network", "url", "icon_preview", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("network", "is_active")
    search_fields = ("custom_name", "url")
    ordering = ("order", "network")

    fieldsets = (
        (
            "Основное",
            {
                "fields": ("network", "url", "custom_name"),
                "description": mark_safe("""
                <div class="help">
                    <strong>📱 Доступные соцсети и иконки:</strong><br>
                    • <strong>Telegram</strong> — <code>bi bi-telegram</code><br>
                    • <strong>WhatsApp</strong> — <code>bi bi-whatsapp</code><br>
                    • <strong>ВКонтакте</strong> — <code>bi bi-vk</code><br>
                    • <strong>Одноклассники</strong> — <code>bi bi-circle-fill</code> (оранжевый)<br>
                    • <strong>YouTube</strong> — <code>bi bi-youtube</code><br>
                    • <strong>Rutube</strong> — <code>bi bi-play-circle</code><br>
                    • <strong>Яндекс.Дзен</strong> — <code>bi bi-pen</code><br>
                    • <strong>Instagram</strong> — <code>bi bi-instagram</code><br>
                    • <strong>Другая</strong> — укажите название вручную
                </div>
            """),
            },
        ),
        ("Настройки", {"fields": ("order", "is_active")}),
    )

    def icon_preview(self, obj):
        if obj.icon_class:
            return format_html('<i class="{}" style="font-size: 1.5rem; color: #FFD700;"></i>', obj.icon_class)
        return "-"

    icon_preview.short_description = "Иконка"


@admin.register(FooterDocument)
class FooterDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "doc_type", "file_preview", "is_active", "created_at")
    list_filter = ("doc_type", "is_active")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("title",)

    fieldsets = (
        ("Основное", {"fields": ("title", "slug", "doc_type")}),
        (
            "Содержимое",
            {
                "fields": ("content", "file"),
                "description": mark_safe("""
                <div class="help">
                    <strong>📄 Типы документов:</strong><br>
                    • <strong>Текстовый</strong> — введите текст в поле ниже<br>
                    • <strong>PDF</strong> — загрузите файл (макс. 5MB)<br>
                    <br>
                    <strong>💡 Можно использовать оба варианта:</strong><br>
                    Текст будет показан на странице, PDF — для скачивания
                </div>
            """),
            },
        ),
        ("Статус", {"fields": ("is_active",)}),
    )

    def file_preview(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank" class="button">📄 Скачать PDF</a>', obj.file.url)
        return "—"

    file_preview.short_description = "Файл"


@admin.register(HeroImage)
class HeroImageAdmin(admin.ModelAdmin):
    list_display = ("key", "image_preview", "file_size", "updated_at")
    readonly_fields = ("key", "updated_at", "image_preview", "file_size")

    fieldsets = (
        (
            "Информация",
            {
                "fields": ("key", "image", "image_preview", "file_size", "updated_at"),
                "description": mark_safe("""
                <div class="help" style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff;">
                    <h5 style="margin-top: 0;">📐 Требования к изображению:</h5>
                    <ul style="margin-bottom: 0; padding-left: 20px;">
                        <li><strong>Размер:</strong> 1920×800px (рекомендуется)</li>
                        <li><strong>Минимум:</strong> 1600×600px</li>
                        <li><strong>Максимальный вес:</strong> 2MB</li>
                        <li><strong>Форматы:</strong> JPG, PNG, WEBP</li>
                    </ul>
                    <br>
                    <strong>💡 Советы:</strong>
                    <ul style="margin-bottom: 0; padding-left: 20px;">
                        <li>Используйте фото интерьера с тёплым освещением</li>
                        <li>Избегайте людей на переднем плане</li>
                        <li>Текст должен хорошо читаться на фоне</li>
                        <li>Используйте пустые столики</li>
                    </ul>
                </div>
            """),
            },
        ),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 200px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);"/>',
                obj.image.url,
            )
        return "Изображение не загружено"

    image_preview.short_description = "Превью"

    def file_size(self, obj):
        if obj.image:
            size_kb = obj.image.size / 1024
            if size_kb < 1024:
                return f"{size_kb:.1f} KB"
            return f"{size_kb / 1024:.2f} MB"
        return "-"

    file_size.short_description = "Размер файла"

    def has_add_permission(self, request):
        return not HeroImage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
