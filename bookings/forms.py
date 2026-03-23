from datetime import datetime, timedelta

from django import forms
from django.utils import timezone

from core.utils import (
    get_max_booking_duration,
    get_min_booking_duration,
    get_restaurant_settings,
)

from .models import Reservation, Table


class ReservationForm(forms.ModelForm):
    """Форма создания бронирования"""

    date = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control", "min": timezone.now().date().isoformat()}
        ),
        label="Дата",
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}), label="Время начала"
    )
    duration = forms.IntegerField(
        min_value=1,
        max_value=5,
        initial=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 5, "value": 2}),
        label="Длительность (часов)",
        help_text="От 1 до 5 часов",
    )
    guests_count = forms.IntegerField(
        min_value=1,
        max_value=20,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 20}),
        label="Количество гостей",
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Пожелания (необязательно)"}),
        label="Комментарий",
    )

    class Meta:
        model = Reservation
        fields = ["date", "time", "duration", "guests_count", "comment"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].widget.attrs["min"] = timezone.now().date().isoformat()

        # Динамически устанавливаем min/max для duration
        min_duration = get_min_booking_duration()
        max_duration = get_max_booking_duration()
        self.fields["duration"].min_value = min_duration
        self.fields["duration"].max_value = max_duration
        self.fields["duration"].help_text = f"От {min_duration} до {max_duration} часов"

    def clean_date(self):
        """Проверка даты"""
        date = self.cleaned_data.get("date")
        if date and date < timezone.now().date():
            raise forms.ValidationError("Нельзя забронировать столик на прошедшую дату")
        return date

    def clean_time(self):
        """Проверка времени"""
        time_value = self.cleaned_data.get("time")
        settings = get_restaurant_settings()
        opening_time = settings.opening_time
        closing_time = settings.closing_time

        if time_value:
            # Если закрывается на следующий день (например, 18:00 - 01:00)
            if settings.closes_next_day:
                # Разрешаем бронирование до closing_time следующего дня
                if time_value < opening_time and time_value < closing_time:
                    # Время до открытия (например, 10:00 при открытии 18:00)
                    raise forms.ValidationError(f'Ресторан открывается в {opening_time.strftime("%H:%M")}')
            else:
                # Обычный режим (закрывается в тот же день)
                if time_value < opening_time:
                    raise forms.ValidationError(f'Ресторан открывается в {opening_time.strftime("%H:%M")}')
                if time_value >= closing_time:
                    raise forms.ValidationError(
                        f'Последнее бронирование должно быть до {closing_time.strftime("%H:%M")}'
                    )

        return time_value

    def clean_duration(self):
        """Проверка длительности"""
        duration = self.cleaned_data.get("duration")
        min_duration = get_min_booking_duration()
        max_duration = get_max_booking_duration()

        if duration and (duration < min_duration or duration > max_duration):
            raise forms.ValidationError(f"Длительность должна быть от {min_duration} до {max_duration} часов")
        return duration

    def clean(self):
        """Комплексная проверка времени и длительности"""
        cleaned_data = super().clean()
        time_value = cleaned_data.get("time")
        duration = cleaned_data.get("duration")
        date = cleaned_data.get("date")

        if time_value and duration and date:
            settings = get_restaurant_settings()
            opening_time = settings.opening_time

            # Создаём datetime начала и окончания
            start_datetime = datetime.combine(date, time_value)
            end_datetime = start_datetime + timedelta(hours=duration)

            # Получаем datetime закрытия (с учётом следующего дня)
            closing_datetime = datetime.combine(date, settings.closing_time)
            if settings.closes_next_day:
                closing_datetime += timedelta(days=1)

            # Проверяем, что начало не раньше открытия
            opening_datetime = datetime.combine(date, opening_time)
            if start_datetime < opening_datetime:
                raise forms.ValidationError({"time": f'Ресторан открывается в {opening_time.strftime("%H:%M")}'})

            # Проверяем, что окончание не позже закрытия
            if end_datetime > closing_datetime:
                # Считаем максимальную длительность
                max_delta = closing_datetime - start_datetime
                max_hours = max_delta.total_seconds() // 3600

                closing_display = closing_datetime.strftime("%H:%M")
                if closing_datetime.date() > date:
                    closing_display += " (+1)"

                end_display = end_datetime.strftime("%H:%M")
                if end_datetime.date() > date:
                    end_display += " (+1)"

                raise forms.ValidationError(
                    {
                        "duration": f"Бронирование закончится в {end_display}, "
                        f"что после закрытия ({closing_display}). "
                        f"Максимальная длительность — {int(max_hours)} ч."
                    }
                )

        return cleaned_data


class TableChoiceForm(forms.Form):
    """Форма выбора столика"""

    table = forms.ModelChoiceField(
        queryset=Table.objects.filter(is_active=True),
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label="Выберите столик",
        empty_label=None,
    )

    def __init__(self, *args, date=None, time=None, guests_count=None, duration=None, **kwargs):
        super().__init__(*args, **kwargs)

        if guests_count:
            self.fields["table"].queryset = self.fields["table"].queryset.filter(capacity__gte=guests_count)

        if date and time and duration:
            available_tables = []
            for table in self.fields["table"].queryset:
                if table.is_available(date, time, duration):
                    available_tables.append(table.id)
            self.fields["table"].queryset = self.fields["table"].queryset.filter(id__in=available_tables)
        elif date and time:
            available_tables = []
            for table in self.fields["table"].queryset:
                if table.is_available(date, time):
                    available_tables.append(table.id)
            self.fields["table"].queryset = self.fields["table"].queryset.filter(id__in=available_tables)
