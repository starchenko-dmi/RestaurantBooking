from .models import RestaurantSettings
from datetime import datetime, timedelta


def get_restaurant_settings():
    """Получить настройки ресторана"""
    return RestaurantSettings.get_settings()


def get_opening_time():
    """Получить время открытия"""
    return get_restaurant_settings().opening_time


def get_closing_time():
    """Получить время закрытия"""
    return get_restaurant_settings().closing_time


def get_closing_datetime(date):
    """Получить datetime закрытия для данной даты"""
    return get_restaurant_settings().get_closing_datetime(date)


def get_min_booking_duration():
    """Получить мин. длительность бронирования"""
    return get_restaurant_settings().min_booking_duration


def get_max_booking_duration():
    """Получить макс. длительность бронирования"""
    return get_restaurant_settings().max_booking_duration