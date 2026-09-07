from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserRegistrationTests(TestCase):
    """Тесты регистрации"""

    def setUp(self):
        self.client = Client()

    def test_register_view_get(self):
        """Проверка отображения страницы регистрации"""
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")

    def test_register_view_post_valid(self):
        """Проверка успешной регистрации"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
        }
        response = self.client.post(reverse("users:register"), data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("core:home"))

        # Проверяем, что пользователь создан
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_view_post_invalid(self):
        """Проверка регистрации с невалидными данными"""
        data = {
            "username": "test",
            "email": "invalid-email",
            "password1": "123",
            "password2": "456",
        }
        response = self.client.post(reverse("users:register"), data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")
        self.assertFalse(User.objects.filter(username="test").exists())

    def test_register_authenticated_user(self):
        """Проверка, что авторизованный пользователь не может зарегистрироваться"""
        User.objects.create_user(username="existing", password="pass123")
        self.client.login(username="existing", password="pass123")

        response = self.client.get(reverse("users:register"))
        self.assertRedirects(response, reverse("core:home"))


class UserLoginTests(TestCase):
    """Тесты входа"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

    def test_login_view_get(self):
        """Проверка отображения страницы входа"""
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_login_view_post_valid(self):
        """Проверка успешного входа"""
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(reverse("users:login"), data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("core:home"))

    def test_login_view_post_invalid(self):
        """Проверка входа с неверным паролем"""
        data = {"username": "testuser", "password": "wrongpass"}
        response = self.client.post(reverse("users:login"), data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_login_authenticated_user(self):
        """Проверка, что авторизованный пользователь перенаправляется"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(reverse("users:login"))
        self.assertRedirects(response, reverse("core:home"))


class UserLogoutTests(TestCase):
    """Тесты выхода"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_logout_view(self):
        """Проверка выхода"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(reverse("users:logout"))

        self.assertRedirects(response, reverse("core:home"))
        # Проверяем, что пользователь вышел
        self.assertNotIn("_auth_user_id", self.client.session)


class ProfileTests(TestCase):
    """Тесты профиля"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

    def test_profile_view_requires_login(self):
        """Проверка, что профиль требует авторизации"""
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_profile_view_authenticated(self):
        """Проверка отображения профиля"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(reverse("users:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")
        self.assertContains(response, "testuser")

    def test_profile_edit_view(self):
        """Проверка редактирования профиля"""
        self.client.login(username="testuser", password="testpass123")

        data = {"first_name": "Test", "last_name": "User", "email": "newemail@example.com", "phone": "+79990000000"}
        response = self.client.post(reverse("users:profile_edit"), data)

        self.assertRedirects(response, reverse("users:profile"))

        # Проверяем, что данные обновлены
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Test")
        self.assertEqual(self.user.email, "newemail@example.com")

    def test_profile_delete_view(self):
        """Проверка удаления профиля"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(reverse("users:profile_delete"))

        self.assertRedirects(response, reverse("core:home"))
        self.assertFalse(User.objects.filter(username="testuser").exists())
