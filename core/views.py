from django.shortcuts import render
from django.conf import settings as django_settings
from core.models import SiteContent, TeamMember, Service
from core.utils import get_content, get_restaurant_settings


def home(request):
    """Главная страница"""
    context = {
        'title': get_content('home_title', 'Добро пожаловать в наш ресторан'),
        'description': get_content('home_description', 'Лучшая кухня в городе'),
        'services': Service.objects.filter(is_active=True)[:3],
        'about_text': get_content('about_history', 'История нашего ресторана начинается с мечты...')[:200] + '...',
        'banner': None,
    }
    return render(request, 'core/home.html', context)


def about(request):
    """Страница 'О ресторане'"""
    context = {
        'title': get_content('about_title', 'О нашем ресторане'),
        'history': get_content('about_history',
                               'Наш ресторан был основан в 2010 году. Мы стремимся дарить гостям незабываемые впечатления и изысканную кухню.'),
        'mission': get_content('about_mission',
                               'Наша миссия — создавать атмосферу уюта и гостеприимства, где каждый гость чувствует себя как дома.'),
        'team': TeamMember.objects.filter(is_active=True).order_by('order'),
    }
    return render(request, 'core/about.html', context)


def contacts(request):
    """Страница контактов"""
    restaurant_settings = get_restaurant_settings()

    context = {
        'title': get_content('contacts_title', 'Контакты'),
        'settings': restaurant_settings,
        'yandex_maps_api_key': django_settings.YANDEX_MAPS_API_KEY,
    }
    return render(request, 'core/contacts.html', context)