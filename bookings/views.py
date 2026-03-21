from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime, time as time_class  # ← Добавили импорты
from .models import Reservation, Table
from .forms import ReservationForm, TableChoiceForm


def reservation_create(request):
    """Создание бронирования (доступно всем)"""

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time_value = form.cleaned_data['time']  # ← Переименовали
            guests_count = form.cleaned_data['guests_count']

            available_tables = Table.objects.filter(
                is_active=True,
                capacity__gte=guests_count
            )

            available_table_ids = []
            for table in available_tables:
                if table.is_available(date, time_value):
                    available_table_ids.append(table.id)

            if not available_table_ids:
                messages.error(request, 'К сожалению, нет свободных столиков на это время. Выберите другое время.')
                return render(request, 'bookings/reservation_create.html', {'form': form})

            request.session['reservation_data'] = {
                'date': date.isoformat(),
                'time': time_value.isoformat(),  # ← Сохраняем в ISO формате
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

    # Исправлено: парсим время правильно
    time_str = reservation_data['time']
    if 'T' in time_str:
        # Полный ISO формат (2024-03-21T18:00:00)
        time_value = timezone.datetime.fromisoformat(time_str).time()
    else:
        # Только время (18:00:00 или 18:00)
        if len(time_str) == 5:  # 18:00
            time_value = datetime.strptime(time_str, '%H:%M').time()
        else:  # 18:00:00
            time_value = datetime.strptime(time_str, '%H:%M:%S').time()

    guests_count = reservation_data['guests_count']

    if request.method == 'POST':
        form = TableChoiceForm(request.POST, date=date, time=time_value, guests_count=guests_count)
        if form.is_valid():
            table = form.cleaned_data['table']

            end_time_value = (datetime.combine(date, time_value) + timedelta(hours=2)).time()

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

            messages.success(request, f'Столик {table.number} забронирован! Ожидайте подтверждения.')
            return redirect('bookings:reservation_detail', pk=reservation.pk)
    else:
        form = TableChoiceForm(date=date, time=time_value, guests_count=guests_count)

    return render(request, 'bookings/table_select.html', {
        'form': form,
        'date': date,
        'time': time_value,
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
