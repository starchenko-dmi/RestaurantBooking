from django.contrib import admin
from .models import SiteContent, TeamMember, Service


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
