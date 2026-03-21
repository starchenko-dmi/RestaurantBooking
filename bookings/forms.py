from django import forms
from django.utils import timezone
from datetime import datetime, time as time_class, timedelta
from .models import Reservation, Table


class ReservationForm(forms.ModelForm):
    """Форма создания бронирования"""

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date().isoformat()
        }),
        label='Дата'
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        }),
        label='Время начала'
    )
    duration = forms.IntegerField(
        min_value=1,
        max_value=5,
        initial=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 5,
            'value': 2
        }),
        label='Длительность (часов)',
        help_text='От 1 до 5 часов'
    )
    guests_count = forms.IntegerField(
        min_value=1,
        max_value=20,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 20
        }),
        label='Количество гостей'
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Пожелания (необязательно)'
        }),
        label='Комментарий'
    )

    class Meta:
        model = Reservation
        fields = ['date', 'time', 'duration', 'guests_count', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['min'] = timezone.now().date().isoformat()

    def clean_date(self):
        """Проверка даты"""
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise forms.ValidationError('Нельзя забронировать столик на прошедшую дату')
        return date

    def clean_time(self):
        """Проверка времени"""
        time_value = self.cleaned_data.get('time')
        if time_value:
            # Ресторан работает с 10:00 до 23:00
            if time_value < time_class(10, 0):
                raise forms.ValidationError('Ресторан открывается в 10:00')
            if time_value >= time_class(22, 0):
                raise forms.ValidationError(
                    'Последнее бронирование должно начинаться не позже 22:00 (минимум 1 час до закрытия)')
        return time_value

    def clean_duration(self):
        """Проверка длительности"""
        duration = self.cleaned_data.get('duration')
        if duration and (duration < 1 or duration > 5):
            raise forms.ValidationError('Длительность должна быть от 1 до 5 часов')
        return duration

    def clean(self):
        """Комплексная проверка времени и длительности"""
        cleaned_data = super().clean()
        time_value = cleaned_data.get('time')
        duration = cleaned_data.get('duration')
        date = cleaned_data.get('date')  # ← Получаем дату бронирования

        if time_value and duration and date:
            # Рассчитываем время окончания на основе ДАТЫ БРОНИРОВАНИЯ
            end_datetime = datetime.combine(date, time_value) + timedelta(hours=duration)
            end_time = end_datetime.time()

            # Проверяем, что окончание не позже 23:00
            if end_time > time_class(23, 0):
                raise forms.ValidationError({
                    'duration': f'Бронирование не может закончиться после 23:00. При выбранном времени {time_value.strftime("%H:%M")} максимальная длительность — {self._get_max_duration(time_value)} ч.'
                })

        return cleaned_data

    def _get_max_duration(self, time_value):
        """Вычисляет максимальную длительность для данного времени"""
        closing_time = time_class(23, 0)
        delta = datetime.combine(timezone.now().date(), closing_time) - datetime.combine(timezone.now().date(),
                                                                                         time_value)
        hours = delta.seconds // 3600
        return min(hours, 5)  # Не больше 5 часов


class TableChoiceForm(forms.Form):
    """Форма выбора столика"""

    table = forms.ModelChoiceField(
        queryset=Table.objects.filter(is_active=True),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Выберите столик',
        empty_label=None
    )

    def __init__(self, *args, date=None, time=None, guests_count=None, duration=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Фильтруем столики по вместимости
        if guests_count:
            self.fields['table'].queryset = self.fields['table'].queryset.filter(
                capacity__gte=guests_count
            )

        # Фильтруем доступные столики
        if date and time and duration:
            available_tables = []
            for table in self.fields['table'].queryset:
                if table.is_available(date, time, duration):
                    available_tables.append(table.id)
            self.fields['table'].queryset = self.fields['table'].queryset.filter(
                id__in=available_tables
            )
        elif date and time:
            available_tables = []
            for table in self.fields['table'].queryset:
                if table.is_available(date, time):
                    available_tables.append(table.id)
            self.fields['table'].queryset = self.fields['table'].queryset.filter(
                id__in=available_tables
            )
