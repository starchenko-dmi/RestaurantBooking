from django import forms
from django.utils import timezone
from datetime import datetime, time as time_class, timedelta  # ← Переименовали импорт
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
        label='Время'
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
        fields = ['date', 'time', 'guests_count', 'comment']

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
        time_value = self.cleaned_data.get('time')  # ← Переименовали переменную
        if time_value:
            # Ресторан работает с 10:00 до 23:00
            if time_value < time_class(10, 0) or time_value > time_class(23, 0):  # ← Используем time_class
                raise forms.ValidationError('Ресторан работает с 10:00 до 23:00')
        return time_value

    def clean_guests_count(self):
        """Проверка количества гостей"""
        guests_count = self.cleaned_data.get('guests_count')
        if guests_count and guests_count < 1:
            raise forms.ValidationError('Количество гостей должно быть не менее 1')
        return guests_count


class TableChoiceForm(forms.Form):
    """Форма выбора столика"""

    table = forms.ModelChoiceField(
        queryset=Table.objects.filter(is_active=True),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Выберите столик',
        empty_label=None
    )

    def __init__(self, *args, date=None, time=None, guests_count=None, **kwargs):
        super().__init__(*args, **kwargs)

        if guests_count:
            self.fields['table'].queryset = self.fields['table'].queryset.filter(
                capacity__gte=guests_count
            )

        if date and time:
            available_tables = []
            for table in self.fields['table'].queryset:
                if table.is_available(date, time):
                    available_tables.append(table.id)
            self.fields['table'].queryset = self.fields['table'].queryset.filter(
                id__in=available_tables
            )
