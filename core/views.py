from django.shortcuts import render
from .models import SiteContent, TeamMember, Service


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
    """Страница контактов"""
    context = {
        'title': get_content('contacts_title', 'Контакты'),
        'address': get_content('contacts_address', 'г. Москва, ул. Примерная, 1'),
        'phone': get_content('contacts_phone', '+7 (999) 000-00-00'),
        'email': get_content('contacts_email', 'info@restaurant.ru'),
        'work_hours': get_content('contacts_work_hours', 'Ежедневно с 10:00 до 23:00'),
        'map': get_content('contacts_map'),
    }
    return render(request, 'core/contacts.html', context)
