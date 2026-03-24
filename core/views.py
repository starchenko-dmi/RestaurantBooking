from .models import FooterDocument
from django.contrib import messages
from django.conf import settings as django_settings
from django.shortcuts import get_object_or_404, render, redirect
from core.models import Service, TeamMember
from core.utils import get_content, get_restaurant_settings
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm



def home(request):
    """Главная страница"""
    context = {
        "title": get_content("home_title", "Добро пожаловать в наш ресторан"),
        "description": get_content("home_description", "Лучшая кухня в городе"),
        "services": Service.objects.filter(is_active=True)[:3],
        "about_text": get_content("about_history", "История нашего ресторана начинается с мечты...")[:200] + "...",
        "banner": None,
    }
    return render(request, "core/home.html", context)


def about(request):
    """Страница 'О ресторане'"""
    context = {
        "title": get_content("about_title", "О нашем ресторане"),
        "history": get_content(
            "about_history",
            "Наш ресторан был основан в 2010 году. Мы стремимся дарить гостям незабываемые впечатления и изысканную кухню.",
        ),
        "mission": get_content(
            "about_mission",
            "Наша миссия — создавать атмосферу уюта и гостеприимства, где каждый гость чувствует себя как дома.",
        ),
        "team": TeamMember.objects.filter(is_active=True).order_by("order"),
    }
    return render(request, "core/about.html", context)


def contacts(request):
    """Страница контактов"""
    restaurant_settings = get_restaurant_settings()

    from django.core.mail import send_mail
    from django.core.exceptions import ImproperlyConfigured

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            try:
                send_mail(
                    subject=f'Новое сообщение от {name}',
                    message=f'От: {email}\n\nСообщение:\n{message}',
                    from_email=django_settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[restaurant_settings.email],
                    fail_silently=False,
                )
                messages.success(request, 'Спасибо! Ваше сообщение отправлено.')
            except Exception as e:
                messages.error(request, f'Ошибка отправки: {e}')
                # Для отладки — выведи в консоль
                print(f"❌ EMAIL ERROR: {type(e).__name__}: {e}")

            return redirect('core:contacts')
    else:
        form = ContactForm()  # ← Создаём ПУСТУЮ форму для GET запроса

    context = {
        'title': get_content('contacts_title', 'Контакты'),
        'settings': restaurant_settings,
        'yandex_maps_api_key': django_settings.YANDEX_MAPS_API_KEY,
        'form': form,
    }
    return render(request, 'core/contacts.html', context)


def document_view(request, slug):
    """Просмотр документа (оферта, политика и т.д.)"""
    document = get_object_or_404(FooterDocument, slug=slug, is_active=True)
    return render(request, "core/document.html", {"document": document})
