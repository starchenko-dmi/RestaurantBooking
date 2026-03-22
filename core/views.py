from django.shortcuts import render
from .models import SiteContent, TeamMember, Service
from core.models import SiteContent
from core.utils import get_restaurant_settings
from django.conf import settings as django_settings


def get_content(key, default=''):
    """Хелпер для получения контента по ключу"""
    try:
        content = SiteContent.objects.get(key=key, is_active=True)
        return content.get_value() or default
    except SiteContent.DoesNotExist:
        return default


def home(request):
    """Главная страница ресторана"""
    context = {
        'title': get_content('home_title', 'Добро пожаловать в наш ресторан'),
        'description': get_content('home_description', 'Лучшая кухня в городе'),
        'banner': get_content('home_banner'),
        'services': Service.objects.filter(is_active=True),
        'about_text': get_content('about_short', 'О нашем ресторане'),
    }
    return render(request, 'core/home.html', context)


def about(request):
    """Страница 'О ресторане'"""
    context = {
        'title': get_content('about_title', 'О нашем ресторане'),
        'history': get_content('about_history', 'История ресторана'),
        'mission': get_content('about_mission', 'Наша миссия'),
        'team': TeamMember.objects.filter(is_active=True),
        'banner': get_content('about_banner'),
    }
    return render(request, 'core/about.html', context)


def contacts(request):

    restaurant_settings = get_restaurant_settings()
    api_key = django_settings.YANDEX_MAPS_API_KEY

    context = {
        'title': get_content('contacts_title', 'Контакты'),
        'settings': restaurant_settings,
        'yandex_maps_api_key': api_key,
    }
    return render(request, 'core/contacts.html', context)
