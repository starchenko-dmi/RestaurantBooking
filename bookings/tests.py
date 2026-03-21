from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, time, timedelta
from .models import Table, Reservation


User = get_user_model()


class TableModelTest(TestCase):
    """Тесты модели Table"""

    def setUp(self):
        self.table = Table.objects.create(
            number='1',
            capacity=4,
            zone='main'
        )

    def test_table_creation(self):
        """Проверка создания столика"""
        self.assertEqual(self.table.number, '1')
        self.assertEqual(self.table.capacity, 4)
        self.assertEqual(str(self.table), 'Столик 1 (Основной зал, 4 чел.)')

    def test_unique_number(self):
        """Проверка уникальности номера"""
        with self.assertRaises(Exception):
            Table.objects.create(
                number='1',
                capacity=2
            )


class ReservationModelTest(TestCase):
    """Тесты модели Reservation"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.table = Table.objects.create(
            number='1',
            capacity=4,
            zone='main'
        )
        self.tomorrow = timezone.now().date() + timedelta(days=1)

        self.reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=self.tomorrow,
            time=time(18, 0),
            end_time=time(20, 0),
            guests_count=2
        )

    def test_reservation_creation(self):
        """Проверка создания бронирования"""
        self.assertEqual(self.reservation.user, self.user)
        self.assertEqual(self.reservation.table, self.table)
        self.assertEqual(self.reservation.status, 'pending')

    def test_guests_validation(self):
        """Проверка валидации количества гостей"""
        reservation = Reservation(
            user=self.user,
            table=self.table,
            date=self.tomorrow,
            time=time(20, 0),
            end_time=time(22, 0),
            guests_count=10  # Больше вместимости
        )
        with self.assertRaises(Exception):
            reservation.full_clean()

    def test_overlapping_reservation(self):
        """Проверка запрета пересекающихся бронирований"""
        reservation = Reservation(
            user=self.user,
            table=self.table,
            date=self.tomorrow,
            time=time(19, 0),  # Пересекается с 18:00-20:00
            end_time=time(21, 0),
            guests_count=2
        )
        with self.assertRaises(Exception):
            reservation.full_clean()

    def test_non_overlapping_reservation(self):
        """Проверка разрешения непересекающихся бронирований"""
        reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=self.tomorrow,
            time=time(20, 0),  # Начинается после окончания первого
            end_time=time(22, 0),
            guests_count=2
        )
        self.assertEqual(reservation.status, 'pending')

    def test_cancel_reservation(self):
        """Проверка отмены бронирования"""
        self.reservation.cancel()
        self.assertEqual(self.reservation.status, 'cancelled')

    def test_confirm_reservation(self):
        """Проверка подтверждения бронирования"""
        self.reservation.confirm()
        self.assertEqual(self.reservation.status, 'confirmed')

    def test_can_cancel(self):
        """Проверка возможности отмены"""
        self.assertTrue(self.reservation.can_cancel())

        # Отменённое нельзя отменить
        self.reservation.cancel()
        self.assertFalse(self.reservation.can_cancel())


class TableAvailabilityTest(TestCase):
    """Тесты доступности столиков"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.table = Table.objects.create(
            number='1',
            capacity=4,
            zone='main'
        )
        self.tomorrow = timezone.now().date() + timedelta(days=1)

    def test_table_available_when_no_reservations(self):
        """Столик свободен, если нет бронирований"""
        is_available = self.table.is_available(
            self.tomorrow,
            time(18, 0)
        )
        self.assertTrue(is_available)

    def test_table_not_available_when_booked(self):
        """Столик занят, если есть бронирование"""
        Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=self.tomorrow,
            time=time(18, 0),
            end_time=time(20, 0),
            guests_count=2,
            status='confirmed'
        )

        is_available = self.table.is_available(
            self.tomorrow,
            time(18, 30)  # Внутри диапазона
        )
        self.assertFalse(is_available)

    def test_table_available_before_reservation(self):
        """Столик свободен до бронирования"""
        Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=self.tomorrow,
            time=time(18, 0),
            end_time=time(20, 0),
            guests_count=2
        )

        is_available = self.table.is_available(
            self.tomorrow,
            time(16, 0)  # До бронирования
        )
        self.assertTrue(is_available)

    def test_table_available_after_reservation(self):
        """Столик свободен после бронирования"""
        Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=self.tomorrow,
            time=time(18, 0),
            end_time=time(20, 0),
            guests_count=2
        )

        is_available = self.table.is_available(
            self.tomorrow,
            time(20, 0)  # После окончания
        )
        self.assertTrue(is_available)


class ReservationViewTests(TestCase):
    """Тесты для views бронирования"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.table = Table.objects.create(
            number='1',
            capacity=4,
            zone='main',
            is_active=True
        )
        self.tomorrow = timezone.now().date() + timedelta(days=1)

    def test_reservation_create_view_get(self):
        """Проверка отображения формы бронирования"""
        response = self.client.get(reverse('bookings:reservation_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/reservation_create.html')
        self.assertContains(response, 'Бронирование столика')

    def test_reservation_create_view_post_valid(self):
        """Проверка создания бронирования с валидными данными"""
        # Авторизуем пользователя
        self.client.login(username='testuser', password='testpass123')

        data = {
            'date': self.tomorrow.isoformat(),
            'time': '18:00',
            'guests_count': 2,
            'comment': 'Тестовое бронирование'
        }
        response = self.client.post(reverse('bookings:reservation_create'), data)

        # Должна быть переадресация на выбор столика
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('bookings:table_select'), fetch_redirect_response=False)

        # Проверяем, что данные сохранены в сессии
        session = self.client.session
        self.assertIn('reservation_data', session)

    def test_reservation_create_view_post_invalid_date(self):
        """Проверка отклонения прошедшей даты"""
        data = {
            'date': (timezone.now().date() - timedelta(days=1)).isoformat(),
            'time': '18:00',
            'guests_count': 2
        }
        response = self.client.post(reverse('bookings:reservation_create'), data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/reservation_create.html')
        self.assertContains(response, 'Нельзя забронировать столик на прошедшую дату')

    def test_table_select_view_requires_login(self):
        """Проверка, что выбор столика требует авторизации"""
        # Устанавливаем данные сессии
        session = self.client.session
        session['reservation_data'] = {
            'date': self.tomorrow.isoformat(),
            'time': '18:00',
            'guests_count': 2,
            'comment': ''
        }
        session.save()

        response = self.client.get(reverse('bookings:table_select'))

        # Должна быть переадресация на вход
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_table_select_view_no_session_data(self):
        """Проверка, что без данных сессии нельзя выбрать столик"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('bookings:table_select'))

        # Должна быть переадресация на форму бронирования
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('bookings:reservation_create'))

    def test_table_select_view_post_valid(self):
        """Проверка успешного выбора столика"""
        self.client.login(username='testuser', password='testpass123')

        # Устанавливаем данные сессии
        session = self.client.session
        session['reservation_data'] = {
            'date': self.tomorrow.isoformat(),
            'time': '18:00',
            'guests_count': 2,
            'comment': 'Тест'
        }
        session.save()

        data = {'table': self.table.id}
        response = self.client.post(reverse('bookings:table_select'), data)

        # Должна быть переадресация на детали бронирования
        self.assertEqual(response.status_code, 302)

        # Проверяем, что бронирование создано
        reservation = Reservation.objects.first()
        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.user, self.user)
        self.assertEqual(reservation.table, self.table)
        self.assertEqual(reservation.status, 'pending')

        # Проверяем, что сессия очищена
        session = self.client.session
        self.assertNotIn('reservation_data', session)

    def test_reservation_list_view_requires_login(self):
        """Проверка, что список бронирований требует авторизации"""
        response = self.client.get(reverse('bookings:reservation_list'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_reservation_list_view_authenticated(self):
        """Проверка отображения списка бронирований"""
        self.client.login(username='testuser', password='testpass123')

        # Создаём тестовое бронирование
        Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=self.tomorrow,
            time=time(18, 0),
            end_time=time(20, 0),
            guests_count=2,
            status='confirmed'
        )

        response = self.client.get(reverse('bookings:reservation_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/reservation_list.html')
        self.assertContains(response, 'Столик 1')

    def test_reservation_detail_view_requires_login(self):
        """Проверка, что детали бронирования требуют авторизации"""
        reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=self.tomorrow,
            time=time(18, 0),
            end_time=time(20, 0),
            guests_count=2
        )

        response = self.client.get(reverse('bookings:reservation_detail', args=[reservation.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_reservation_detail_view_owner(self):
        """Проверка, что пользователь видит только свои бронирования"""
        self.client.login(username='testuser', password='testpass123')

        reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=self.tomorrow,
            time=time(18, 0),
            end_time=time(20, 0),
            guests_count=2
        )

        response = self.client.get(reverse('bookings:reservation_detail', args=[reservation.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/reservation_detail.html')
        self.assertContains(response, f'Бронирование #{reservation.id}')

    def test_reservation_detail_view_not_owner(self):
        """Проверка, что нельзя чужие бронирования"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        self.client.login(username='otheruser', password='otherpass123')

        reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=self.tomorrow,
            time=time(18, 0),
            end_time=time(20, 0),
            guests_count=2
        )

        response = self.client.get(reverse('bookings:reservation_detail', args=[reservation.pk]))

        self.assertEqual(response.status_code, 404)

    def test_reservation_cancel_view_requires_login(self):
        """Проверка, что отмена требует авторизации"""
        reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=self.tomorrow,
            time=time(18, 0),
            end_time=time(20, 0),
            guests_count=2
        )

        response = self.client.get(reverse('bookings:reservation_cancel', args=[reservation.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_reservation_cancel_view_post(self):
        """Проверка отмены бронирования"""
        self.client.login(username='testuser', password='testpass123')

        reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=self.tomorrow,
            time=time(18, 0),
            end_time=time(20, 0),
            guests_count=2,
            status='confirmed'
        )

        response = self.client.post(reverse('bookings:reservation_cancel', args=[reservation.pk]))

        self.assertRedirects(response, reverse('bookings:reservation_list'))

        # Проверяем, что статус изменился
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, 'cancelled')

    def test_reservation_cancel_view_get_shows_confirmation(self):
        """Проверка отображения страницы подтверждения отмены"""
        self.client.login(username='testuser', password='testpass123')

        reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=self.tomorrow,
            time=time(18, 0),
            end_time=time(20, 0),
            guests_count=2
        )

        response = self.client.get(reverse('bookings:reservation_cancel', args=[reservation.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/reservation_confirm_cancel.html')
        self.assertContains(response, 'Отмена бронирования')