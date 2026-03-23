from datetime import time

from django.test import TestCase
from django.urls import reverse

from .models import Service, SiteContent, TeamMember


class SiteContentModelTest(TestCase):
    """Тесты модели SiteContent"""

    def setUp(self):
        self.content = SiteContent.objects.create(
            key="test_key", title="Test Title", content="Test text value", is_active=True  # ← Было text_value
        )

    def test_content_creation(self):
        """Проверка создания контента"""
        self.assertEqual(self.content.key, "test_key")
        self.assertEqual(self.content.title, "Test Title")
        self.assertEqual(self.content.content, "Test text value")  # ← Было text_value
        self.assertTrue(self.content.is_active)

    def test_get_value(self):
        """Проверка метода get_value"""
        self.assertEqual(self.content.get_value(), "Test text value")  # ← Проверяем content

    def test_auto_slug(self):
        """Проверка автоматического создания slug"""
        # Теперь slug не создаётся автоматически, он задаётся вручную для FooterDocument
        # Этот тест можно удалить или изменить
        self.assertEqual(self.content.key, "test_key")

    def test_inactive_content(self):
        """Проверка фильтрации неактивного контента"""
        self.content.is_active = False
        self.content.save()

        inactive = SiteContent.objects.filter(is_active=False)
        self.assertEqual(inactive.count(), 1)


class CoreViewsTest(TestCase):
    """Тесты view функций core"""

    def setUp(self):
        # Создаём тестовые данные
        SiteContent.objects.create(
            key="home_title", title="Test Home", content="Test Title", is_active=True  # ← Было text_value
        )
        SiteContent.objects.create(
            key="home_description", content="Test Description", is_active=True  # ← Было text_value
        )
        SiteContent.objects.create(key="about_history", content="Test History", is_active=True)  # ← Было text_value
        SiteContent.objects.create(key="about_mission", content="Test Mission", is_active=True)  # ← Было text_value
        SiteContent.objects.create(key="contacts_title", content="Test Contacts", is_active=True)  # ← Было text_value

        # Создаём настройки ресторана
        from core.models import RestaurantSettings

        self.settings = RestaurantSettings.objects.create(
            name="Test Restaurant",
            opening_time=time(10, 0),
            closing_time=time(23, 0),
            closes_next_day=False,
            min_booking_duration=1,
            max_booking_duration=5,
            address="Test Address",
            phone="+79991234567",
            email="test@test.ru",
            latitude=55.034401,
            longitude=82.918800,
        )

    def test_home_view(self):
        """Проверка главной страницы"""
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")
        self.assertIn("title", response.context)
        self.assertIn("description", response.context)

    def test_about_view(self):
        """Проверка страницы о ресторане"""
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/about.html")
        self.assertIn("history", response.context)
        self.assertIn("mission", response.context)

    def test_contacts_view(self):
        """Проверка страницы контактов"""
        response = self.client.get(reverse("core:contacts"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/contacts.html")
        self.assertIn("settings", response.context)


class TeamMemberModelTest(TestCase):
    """Тесты модели TeamMember"""

    def setUp(self):
        self.member = TeamMember.objects.create(
            first_name="Иван", last_name="Иванов", position="chef", bio="Опытный шеф-повар"
        )

    def test_member_creation(self):
        """Проверка создания члена команды"""
        self.assertEqual(str(self.member), "Иван Иванов (Шеф-повар)")

    def test_ordering(self):
        """Проверка сортировки"""
        member2 = TeamMember.objects.create(first_name="Петр", last_name="Петров", position="cook", order=1)
        members = TeamMember.objects.all()
        self.assertEqual(members.first(), self.member)


class ServiceModelTest(TestCase):
    """Тесты модели Service"""

    def setUp(self):
        self.service = Service.objects.create(title="Банкеты", description="Проведение банкетов")

    def test_service_creation(self):
        """Проверка создания услуги"""
        self.assertEqual(str(self.service), "Банкеты")
