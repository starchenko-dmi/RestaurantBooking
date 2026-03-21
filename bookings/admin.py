from django.contrib import admin
from django.utils.html import format_html
from .models import Table, Reservation


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'zone', 'is_active', 'get_reservations_count')
    list_filter = ('zone', 'is_active')
    search_fields = ('number', 'description')
    list_editable = ('is_active',)

    def get_reservations_count(self, obj):
        """Количество активных бронирований"""
        return obj.reservations.filter(status__in=['pending', 'confirmed']).count()

    get_reservations_count.short_description = 'Активные брони'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'table', 'date', 'time', 'guests_count', 'status', 'created_at')
    list_filter = ('status', 'date', 'table__zone')
    search_fields = ('user__username', 'user__email', 'table__number')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'

    fieldsets = (
        ('Основное', {
            'fields': ('user', 'table', 'date', 'time', 'end_time', 'guests_count')
        }),
        ('Статус', {
            'fields': ('status', 'comment')
        }),
        ('Мета', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['confirm_reservations', 'cancel_reservations']

    def confirm_reservations(self, request, queryset):
        """Массовое подтверждение бронирований"""
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'Подтверждено {updated} бронирований')

    confirm_reservations.short_description = 'Подтвердить выбранные'

    def cancel_reservations(self, request, queryset):
        """Массовая отмена бронирований"""
        updated = queryset.filter(status__in=['pending', 'confirmed']).update(status='cancelled')
        self.message_user(request, f'Отменено {updated} бронирований')

    cancel_reservations.short_description = 'Отменить выбранные'