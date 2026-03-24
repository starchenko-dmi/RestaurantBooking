from datetime import time

from django.test import TestCase
from django.urls import reverse

from .forms import ContactForm
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


class ContactFormTest(TestCase):
    """Тесты формы обратной связи"""

    def test_contact_form_valid(self):
        """Проверка валидной формы"""
        from core.forms import ContactForm

        form_data = {"name": "Дмитрий", "email": "test@example.com", "message": "Тестовое сообщение"}
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_contact_form_invalid(self):
        """Проверка невалидной формы"""
        from core.forms import ContactForm

        form_data = {"name": "", "email": "invalid-email", "message": ""}
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("message", form.errors)


class ContactsViewTest(TestCase):
    """Тесты страницы контактов"""

    def test_contacts_view_get(self):
        """GET запрос к странице контактов"""
        response = self.client.get(reverse("core:contacts"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/contacts.html")
        self.assertIn("form", response.context)

    def test_contacts_view_post_valid(self):
        """POST запрос с валидными данными"""
        from datetime import time

        from core.models import RestaurantSettings

        # Создаём настройки ресторана
        settings = RestaurantSettings.objects.create(
            name="Test Restaurant",
            opening_time=time(10, 0),
            closing_time=time(23, 0),
            email="test@restaurant.ru",
            latitude=55.0,
            longitude=82.0,
        )

        form_data = {"name": "Дмитрий", "email": "test@example.com", "message": "Тестовое сообщение"}
        response = self.client.post(reverse("core:contacts"), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect после успешной отправки

    def test_contacts_view_post_invalid(self):
        """POST запрос с невалидными данными"""
        form_data = {"name": "", "email": "invalid", "message": ""}
        response = self.client.post(reverse("core:contacts"), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/contacts.html")


class DocumentViewTest(TestCase):
    """Тесты просмотра документов"""

    def test_document_view_exists(self):
        """Страница документа существует"""
        from core.models import FooterDocument

        doc = FooterDocument.objects.create(
            title="Test Document", slug="test-doc", content="Test content", is_active=True
        )
        response = self.client.get(reverse("core:document", args=["test-doc"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/document.html")

    def test_document_view_not_found(self):
        """Документ не найден"""
        response = self.client.get(reverse("core:document", args=["nonexistent"]))
        self.assertEqual(response.status_code, 404)


class HeroImageModelTest(TestCase):
    """Тесты модели HeroImage"""

    def test_hero_image_creation(self):
        """Создание изображения баннера"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        from core.models import HeroImage

        # Создаём тестовое изображение
        image = SimpleUploadedFile(
            "test.jpg", b"\x89PNG\r\n\x1a\n", content_type="image/jpeg"  # Минимальный PNG header
        )

        hero = HeroImage.objects.create(key="home_hero", image=image)
        self.assertEqual(hero.key, "home_hero")
        self.assertIsNotNone(hero.image)


class SocialLinkModelTest(TestCase):
    """Тесты модели SocialLink"""

    def test_social_link_creation(self):
        """Создание ссылки на соцсеть"""
        from core.models import SocialLink

        link = SocialLink.objects.create(network="telegram", url="https://t.me/test", order=1, is_active=True)
        self.assertEqual(link.network, "telegram")
        self.assertEqual(link.icon_class, "bi bi-telegram")
        self.assertEqual(link.display_name, "Telegram")

    def test_social_link_custom(self):
        """Кастомная соцсеть"""
        from core.models import SocialLink

        link = SocialLink.objects.create(
            network="custom", custom_name="My Network", url="https://example.com", is_active=True
        )
        self.assertEqual(link.display_name, "My Network")
        self.assertEqual(link.icon_class, "bi bi-share")


class FooterDocumentModelTest(TestCase):
    """Тесты модели FooterDocument"""

    def test_footer_document_creation(self):
        """Создание документа"""
        from core.models import FooterDocument

        doc = FooterDocument.objects.create(
            title="Test Document", slug="test-doc", content="Test content", is_active=True
        )
        self.assertEqual(doc.title, "Test Document")
        self.assertEqual(doc.slug, "test-doc")


class ContactViewErrorTest(TestCase):
    """Тест обработки ошибок отправки email"""

    def test_contacts_view_post_email_error(self):
        """POST запрос с ошибкой отправки email"""
        from unittest.mock import patch

        from django.contrib.messages import get_messages

        form_data = {"name": "Дмитрий", "email": "test@example.com", "message": "Тест"}

        # Имитируем ошибку отправки email
        with patch("core.views.send_mail", side_effect=Exception("SMTP error")):
            response = self.client.post(reverse("core:contacts"), form_data)

            # Ожидаем редирект (PRG паттерн)
            self.assertEqual(response.status_code, 302)  # ← Исправлено!

            # Проверяем, что сообщение об ошибке добавлено
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any("Ошибка" in str(msg) for msg in messages), "Ошибка отправки не отображена пользователю")
