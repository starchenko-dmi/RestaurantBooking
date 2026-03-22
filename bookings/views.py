from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime, time as time_class
from .models import Reservation, Table
from .forms import ReservationForm, TableChoiceForm
from core.utils import get_opening_time, get_closing_time, get_closing_datetime, get_restaurant_settings


def reservation_create(request):
    """Создание бронирования (доступно всем)"""

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time_value = form.cleaned_data['time']
            duration = form.cleaned_data['duration']
            guests_count = form.cleaned_data['guests_count']

            # Получаем настройки
            settings = get_restaurant_settings()
            opening_time = settings.opening_time

            # Создаём datetime объекты
            start_datetime = datetime.combine(date, time_value)
            end_datetime = start_datetime + timedelta(hours=duration)

            # Получаем datetime открытия и закрытия
            opening_datetime = datetime.combine(date, opening_time)
            closing_datetime = datetime.combine(date, settings.closing_time)
            if settings.closes_next_day:
                closing_datetime += timedelta(days=1)

            # Проверяем время начала
            if start_datetime < opening_datetime:
                form.add_error('time', f'Ресторан открывается в {opening_time.strftime("%H:%M")}')
                return render(request, 'bookings/reservation_create.html', {'form': form})

            # Проверяем время окончания
            if end_datetime > closing_datetime:
                max_delta = closing_datetime - start_datetime
                max_hours = int(max_delta.total_seconds() // 3600)

                closing_display = closing_datetime.strftime("%d.%m.%Y в %H:%M")

                form.add_error('duration',
                               f'Бронирование закончится {end_datetime.strftime("%d.%m.%Y в %H:%M")}, '
                               f'что после закрытия ({closing_display}). '
                               f'Максимальная длительность — {max_hours} ч.'
                               )
                return render(request, 'bookings/reservation_create.html', {'form': form})

            end_time_value = end_datetime.time()

            available_tables = Table.objects.filter(
                is_active=True,
                capacity__gte=guests_count
            )

            available_table_ids = []
            for table in available_tables:
                if table.is_available(date, time_value, duration):
                    available_table_ids.append(table.id)

            if not available_table_ids:
                messages.error(request, 'К сожалению, нет свободных столиков на это время. Выберите другое время.')
                return render(request, 'bookings/reservation_create.html', {'form': form})

            request.session['reservation_data'] = {
                'date': date.isoformat(),
                'time': time_value.isoformat(),
                'duration': duration,
                'end_time': end_time_value.isoformat(),
                'guests_count': guests_count,
                'comment': form.cleaned_data.get('comment', '')
            }

            return redirect('bookings:table_select')
    else:
        form = ReservationForm()

    return render(request, 'bookings/reservation_create.html', {'form': form})


@login_required
def table_select(request):
    """Выбор конкретного столика"""

    reservation_data = request.session.get('reservation_data')
    if not reservation_data:
        messages.error(request, 'Сначала заполните форму бронирования')
        return redirect('bookings:reservation_create')

    date = timezone.datetime.fromisoformat(reservation_data['date']).date()

    # Парсим время
    time_str = reservation_data['time']
    if 'T' in time_str:
        time_value = timezone.datetime.fromisoformat(time_str).time()
    else:
        if len(time_str) == 5:
            time_value = datetime.strptime(time_str, '%H:%M').time()
        else:
            time_value = datetime.strptime(time_str, '%H:%M:%S').time()

    # Получаем длительность и время окончания
    duration = reservation_data.get('duration', 2)
    end_time_str = reservation_data.get('end_time')
    if end_time_str:
        if 'T' in end_time_str:
            end_time_value = timezone.datetime.fromisoformat(end_time_str).time()
        else:
            end_time_value = datetime.strptime(end_time_str, '%H:%M:%S').time()
    else:
        end_time_value = (datetime.combine(date, time_value) + timedelta(hours=duration)).time()

    guests_count = reservation_data['guests_count']

    if request.method == 'POST':
        form = TableChoiceForm(request.POST, date=date, time=time_value, guests_count=guests_count, duration=duration)
        if form.is_valid():
            table = form.cleaned_data['table']

            reservation = Reservation.objects.create(
                user=request.user,
                table=table,
                date=date,
                time=time_value,
                end_time=end_time_value,
                guests_count=guests_count,
                comment=reservation_data.get('comment', ''),
                status='pending'
            )

            del request.session['reservation_data']

            messages.success(request, f'Столик {table.number} забронирован на {duration} ч.! Ожидайте подтверждения.')
            return redirect('bookings:reservation_detail', pk=reservation.pk)
    else:
        form = TableChoiceForm(date=date, time=time_value, guests_count=guests_count, duration=duration)

    return render(request, 'bookings/table_select.html', {
        'form': form,
        'date': date,
        'time': time_value,
        'duration': duration,
        'end_time': end_time_value,
        'guests_count': guests_count
    })

@login_required
def reservation_list(request):
    """Список бронирований пользователя"""

    reservations = Reservation.objects.filter(
        user=request.user
    ).order_by('-date', '-time')

    now = timezone.now()
    active = reservations.filter(
        date__gte=now.date(),
        status__in=['pending', 'confirmed']
    )
    archive = reservations.exclude(
        pk__in=active.values_list('pk', flat=True)
    )

    return render(request, 'bookings/reservation_list.html', {
        'active_reservations': active,
        'archive_reservations': archive
    })


@login_required
def reservation_detail(request, pk):
    """Детали бронирования"""

    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

    return render(request, 'bookings/reservation_detail.html', {
        'reservation': reservation
    })


@login_required
def reservation_cancel(request, pk):
    """Отмена бронирования"""

    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

    if request.method == 'POST':
        if reservation.can_cancel():
            reservation.cancel()
            messages.success(request, 'Бронирование отменено')
        else:
            messages.error(request, 'Невозможно отменить это бронирование')

        return redirect('bookings:reservation_list')

    return render(request, 'bookings/reservation_confirm_cancel.html', {
        'reservation': reservation
    })
