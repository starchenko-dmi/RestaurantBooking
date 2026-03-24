# 🍽️ Restaurant Booking System

Система бронирования столиков в ресторане на Django с админ-панелью, Яндекс.Картами, настраиваемым контентом и полной валидацией. Проект разработан как дипломная работа и готов к продакшену.

## ✨ Основные возможности

- **Бронирование столиков**: выбор даты, времени, количества гостей с валидацией доступности в реальном времени
- **Гибкое время работы**: поддержка заведений, работающих после полуночи (`closes_next_day`)
- **Яндекс.Карты**: интерактивная карта с меткой ресторана, координаты настраиваются через админку
- **Управляемый контент**: история, миссия, заголовки, соцсети, документы (оферта, политика) редактируются через админку без изменения кода
- **Социальные сети**: 1–5 ссылок с автоматическими иконками Bootstrap Icons (Telegram, WhatsApp, VK, Rutube и др.)
- **Документы**: текстовые страницы или PDF-файлы (до 5 шт.) с кнопкой скачивания
- **Баннер главной**: загрузка изображения с валидацией (1920×800 px, до 2 MB, форматы JPG/PNG/WEBP)
- **Роли пользователей**: обычные пользователи управляют своими бронированиями, менеджеры имеют расширенный доступ
- **Подтверждение email**: регистрация с верификацией почты
- **Адаптивный дизайн**: коричнево-красная тема, Bootstrap 5, корректное отображение на мобильных устройствах
- **Безопасность**: API-ключи и секреты в `.env`, валидация файлов, защита от CSRF/XSS

## 🛠️ Технологический стек

| Категория | Технологии |
|-----------|-----------|
| **Бэкенд** | Python 3.13, Django 6.0.3, Django REST Framework |
| **База данных** | PostgreSQL 14+ (продакшен), SQLite (разработка) |
| **Фронтенд** | Bootstrap 5.3, Bootstrap Icons, jQuery, Яндекс.Карты API |
| **Контейнеризация** | Docker, Docker Compose |
| **Тестирование** | pytest, coverage.py (покрытие 94%+) |
| **Качество кода** | black, isort, flake8 |
| **Деплой** | Gunicorn, Nginx, Docker Hub |

## 🚀 Быстрый старт

### Требования
- Python 3.13+
- PostgreSQL 14+ (или Docker)
- Poetry (рекомендуется) или pip

### 📁 Структура проекта
restaurant_booking/
├── config/                 # Настройки Django
│   ├── settings.py        # Конфигурация проекта
│   ├── urls.py           # Корневые маршруты
│   └── wsgi.py           # WSGI-сервер
├── core/                  # Основное приложение
│   ├── models.py         # SiteContent, RestaurantSettings, SocialLink, FooterDocument, HeroImage
│   ├── views.py          # View-функции (home, about, contacts)
│   ├── admin.py          # Настройка админки
│   ├── utils.py          # Хелперы: get_content(), get_restaurant_settings()
│   ├── validators.py     # Валидация изображений и файлов
│   ├── context_processors.py # footer_data для всех шаблонов
│   ├── templatetags/     # Кастомные теги: {% get_restaurant_settings %}
│   └── templates/core/   # Шаблоны страниц
├── bookings/              # Приложение бронирований
│   ├── models.py         # Reservation, Table
│   ├── forms.py          # Формы с валидацией
│   ├── views.py          # CRUD для бронирований
│   └── templates/bookings/ # Шаблоны бронирования
├── users/                 # Приложение пользователей
│   ├── models.py         # CustomUser
│   ├── views.py          # Регистрация, вход, профиль
│   └── templates/users/  # Шаблоны аутентификации
├── static/               # Статические файлы (CSS, JS, изображения)
├── media/                # Загруженные пользователем файлы
├── templates/            # Базовые шаблоны (base.html)
├── .env                  # Переменные окружения (не коммитить!)
├── .gitignore           # Исключения для Git
├── requirements.txt     # Зависимости для продакшена
├── pyproject.toml       # Конфигурация Poetry
├── Dockerfile           # Образ для продакшена
├── docker-compose.yml   # Оркестрация контейнеров
└── manage.py            # Точка входа Django

### 🐳 Docker
Сборка образа:
docker-compose build

Запуск контейнеров:
docker-compose up -d

Применение миграций в контейнере:
docker-compose exec web python manage.py migrate

Создание суперпользователя:
docker-compose exec web python manage.py createsuperuser

### Установка

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/starchenko-dmi/restaurant_booking.git
cd restaurant_booking

# 2. Создайте виртуальное окружение и установите зависимости
poetry install  # или: pip install -r requirements.txt

# 3. Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env: SECRET_KEY, DATABASE_URL, YANDEX_MAPS_API_KEY и др.

# 4. Примените миграции
python manage.py migrate

# 5. Создайте суперпользователя
python manage.py createsuperuser

# 6. Соберите статические файлы
python manage.py collectstatic --noinput

# 7. Запустите сервер разработки
python manage.py runserver

