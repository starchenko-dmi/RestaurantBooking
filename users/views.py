from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from bookings.models import Reservation

from .forms import CustomAuthenticationForm, CustomUserCreationForm, ProfileForm

User = get_user_model()


def register_view(request):
    """Регистрация нового пользователя"""

    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            return redirect("core:home")
    else:
        form = CustomUserCreationForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    """Вход пользователя"""

    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"С возвращением, {user.username}!")

            # Перенаправляем на страницу, куда пользователь хотел попасть
            next_url = request.GET.get("next", "core:home")
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()

    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    """Выход пользователя"""

    logout(request)
    messages.info(request, "Вы вышли из системы")
    return redirect("core:home")


@login_required
def profile_view(request):
    """Личный кабинет пользователя"""

    # Получаем активные бронирования пользователя
    active_reservations = Reservation.objects.filter(user=request.user, status__in=["pending", "confirmed"]).order_by(
        "date", "time"
    )[:5]

    # Получаем историю бронирований
    history_reservations = (
        Reservation.objects.filter(user=request.user)
        .exclude(status__in=["pending", "confirmed"])
        .order_by("-date", "-time")[:10]
    )

    context = {
        "active_reservations": active_reservations,
        "history_reservations": history_reservations,
    }

    return render(request, "users/profile.html", context)


@login_required
def profile_edit_view(request):
    """Редактирование профиля"""

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён")
            return redirect("users:profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "users/profile_edit.html", {"form": form})


@login_required
def profile_delete_view(request):
    """Удаление профиля"""

    if request.method == "POST":
        username = request.user.username
        request.user.delete()
        logout(request)
        messages.warning(request, f"Аккаунт {username} удалён")
        return redirect("core:home")

    return render(request, "users/profile_delete.html")
