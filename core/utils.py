from .models import RestaurantSettings, SiteContent


def get_content(key, default=""):
    """
    Хелпер для получения контента по ключу

    Если запись не существует — создаёт её с default значением

    Args:
        key: Ключ контента (например, 'about_history')
        default: Значение по умолчанию

    Returns:
        str: Контент или значение по умолчанию
    """
    try:
        content = SiteContent.objects.get(key=key, is_active=True)
        return content.content or default
    except SiteContent.DoesNotExist:
        # Авто-создаём запись с дефолтным значением
        SiteContent.objects.create(key=key, content=default, is_active=True)
        return default


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
