from django import template

from core.models import RestaurantSettings

register = template.Library()


@register.simple_tag
def get_restaurant_settings():
    """Получить настройки ресторана"""
    return RestaurantSettings.get_settings()
