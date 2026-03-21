from django.test import TestCase
from django.urls import reverse
from .models import SiteContent, TeamMember, Service


class SiteContentModelTest(TestCase):
    """Тесты модели SiteContent"""

    def setUp(self):
        self.content = SiteContent.objects.create(
            key='test_key',
            title='Test Content',
            content_type='text',
            text_value='Test text value'
        )

    def test_content_creation(self):
        """Проверка создания контента"""
        self.assertEqual(self.content.key, 'test_key')
        self.assertEqual(str(self.content), 'Test Content (test_key)')

    def test_get_value(self):
        """Проверка метода get_value"""
        self.assertEqual(self.content.get_value(), 'Test text value')

    def test_auto_slug(self):
        """Проверка автоматического создания slug"""
        content = SiteContent.objects.create(
            title='Auto Slug Test',
            content_type='text',
            text_value='Test'
        )
        self.assertEqual(content.key, 'auto-slug-test')

    def test_inactive_content(self):
        """Проверка фильтрации неактивного контента"""
        self.content.is_active = False
        self.content.save()
        active_content = SiteContent.objects.filter(is_active=True)
        self.assertNotIn(self.content, active_content)


class TeamMemberModelTest(TestCase):
    """Тесты модели TeamMember"""

    def setUp(self):
        self.member = TeamMember.objects.create(
            first_name='Иван',
            last_name='Иванов',
            position='chef',
            bio='Опытный шеф-повар'
        )

    def test_member_creation(self):
        """Проверка создания члена команды"""
        self.assertEqual(str(self.member), 'Иван Иванов (Шеф-повар)')

    def test_ordering(self):
        """Проверка сортировки"""
        member2 = TeamMember.objects.create(
            first_name='Петр',
            last_name='Петров',
            position='cook',
            order=1
        )
        members = TeamMember.objects.all()
        self.assertEqual(members.first(), self.member)


class ServiceModelTest(TestCase):
    """Тесты модели Service"""

    def setUp(self):
        self.service = Service.objects.create(
            title='Банкеты',
            description='Проведение банкетов'
        )

    def test_service_creation(self):
        """Проверка создания услуги"""
        self.assertEqual(str(self.service), 'Банкеты')


class CoreViewsTest(TestCase):
    """Тесты views"""

    def setUp(self):
        SiteContent.objects.create(
            key='home_title',
            title='Home Title',
            content_type='text',
            text_value='Welcome',
            is_active=True
        )

    def test_home_view(self):
        """Проверка главной страницы"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_about_view(self):
        """Проверка страницы о ресторане"""
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/about.html')

    def test_contacts_view(self):
        """Проверка страницы контактов"""
        response = self.client.get(reverse('core:contacts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/contacts.html')
