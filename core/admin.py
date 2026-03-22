from django.contrib import admin
from .models import SiteContent, TeamMember, Service, RestaurantSettings


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'key', 'content_type', 'is_active', 'updated_at')
    list_filter = ('content_type', 'is_active')
    search_fields = ('title', 'key', 'text_value')
    list_editable = ('is_active',)
    prepopulated_fields = {'key': ('title',)}
    fieldsets = (
        ('Основное', {
            'fields': ('title', 'key', 'content_type', 'is_active')
        }),
        ('Контент', {
            'fields': ('text_value', 'image_value')
        }),
        ('Мета', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'position', 'is_active', 'order')
    list_filter = ('position', 'is_active')
    search_fields = ('first_name', 'last_name', 'bio')
    list_editable = ('is_active', 'order')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'order')


@admin.register(RestaurantSettings)
class RestaurantSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'is_active')
        }),
        ('Время работы', {
            'fields': ('opening_time', 'closing_time', 'closes_next_day')
        }),
        ('Параметры бронирования', {
            'fields': (
                'min_booking_duration',
                'max_booking_duration',
                'min_advance_booking',
                'max_advance_booking'
            )
        }),
        ('Мета', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        return not RestaurantSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False