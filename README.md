# 🍽️ Restaurant Booking System

Система бронирования столиков в ресторане на Django с админ-панелью, Яндекс.Картами, настраиваемым контентом и полной валидацией. Проект разработан как дипломная работа и готов к продакшену.

## ✨ Основные возможности

- **Бронирование столиков**: выбор даты, времени, количества гостей с валидацией доступности в реальном времени через метод `is_available()`
- **Гибкое время работы**: поддержка заведений, работающих после полуночи (`closes_next_day`)
- **Яндекс.Карты**: интерактивная карта с меткой ресторана, координаты и API-ключ настраиваются через админку
- **Управляемый контент**: история, миссия, заголовки страниц редактируются через админку без изменения кода (модель `SiteContent`)
- **Социальные сети**: 1–5 ссылок с автоматическими иконками Bootstrap Icons (Telegram, WhatsApp, VK, Rutube и др.) через модель `SocialLink`
- **Документы в футере**: текстовые страницы или PDF-файлы (до 5 шт.) с кнопкой скачивания через модель `FooterDocument`
- **Баннер главной**: загрузка изображения с валидацией (1920×800 px, до 2 MB, форматы JPG/PNG/WEBP) через модель `HeroImage`
- **Форма обратной связи**: отправка сообщений на email ресторана через SMTP с валидацией и уведомлениями
- **Роли пользователей**: обычные пользователи управляют своими бронированиями, менеджеры имеют расширенный доступ через группы Django
- **Адаптивный дизайн**: коричнево-красная тема, Bootstrap 5.3, корректное отображение на мобильных устройствах
- **Безопасность**: API-ключи и секреты в `.env`, валидация файлов, защита от CSRF/XSS, пароли приложений для SMTP

## 🛠️ Технологический стек

| Категория | Технологии |
|-----------|-----------|
| **Бэкенд** | Python 3.13, Django 6.0.3 |
| **База данных** | PostgreSQL 14+ (продакшен), SQLite (разработка) |
| **Фронтенд** | Bootstrap 5.3, Bootstrap Icons, jQuery, Яндекс.Карты API |
| **Контейнеризация** | Docker, Docker Compose |
| **Тестирование** | Django TestCase, coverage.py (покрытие 89.97%) |
| **Качество кода** | black, isort, flake8 (PEP 8) |
| **Деплой** | Gunicorn, Nginx, Docker Hub |



### Требования
- Python 3.13+
- PostgreSQL 14+ (или Docker для контейнеризации)
- Poetry (рекомендуется) или pip для управления зависимостями

## Структура проекта
restaurant_booking/
├── config/                 # Настройки Django
│   ├── settings.py        # Конфигурация проекта
│   ├── urls.py           # Корневые маршруты
│   └── wsgi.py           # WSGI-сервер
├── core/                  # Основное приложение
│   ├── models.py         # SiteContent, RestaurantSettings, SocialLink, FooterDocument, HeroImage
│   ├── views.py          # View-функции (home, about, contacts)
│   ├── forms.py          # ContactForm для обратной связи
│   ├── admin.py          # Настройка админки с превью и подсказками
│   ├── utils.py          # Хелперы: get_content(), get_restaurant_settings()
│   ├── validators.py     # Валидация изображений и файлов
│   ├── context_processors.py # footer_data для всех шаблонов
│   ├── templatetags/     # Кастомные теги: {% get_restaurant_settings %}
│   └── templates/core/   # Шаблоны страниц
├── bookings/              # Приложение бронирований
│   ├── models.py         # Reservation, Table
│   ├── forms.py          # ReservationForm с валидацией
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



## Конфигурация (.env)
### Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

### База данных
DB_NAME=restaurant_db
DB_USER=postgres
DB_PASS=postgres
DB_HOST=db
DB_PORT=5432

### Яндекс.Карты
YANDEX_MAPS_API_KEY=your-yandex-maps-api-key

### Email (SMTP Яндекс для формы обратной связи)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@yandex.ru
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@yandex.ru

### Медиа-файлы
MEDIA_ROOT=media/
MEDIA_URL=/media/

## Настройка через админку (/admin/)
Ресторан → Настройки: адрес, телефон, email, время работы, координаты для карты
Контент → Элементы: история, миссия, заголовки (создаются автоматически при первом запросе)
Соцсети → Ссылки: 1–5 соцсетей с авто-иконками и ссылками
Документы → Документы в подвале: оферта, политика (текст или PDF)
Баннер → Изображение главной: загрузка фото 1920×800 px с валидацией

## Файлы конфигурации
Dockerfile: многоступенчатая сборка, установка зависимостей, сборка статики, запуск через Gunicorn
docker-compose.yml: сервисы web (Django), db (PostgreSQL), nginx (прокси)
.dockerignore: исключение кэша, venv, медиа-файлов из образа

## Безопасность
Все чувствительные данные (секретные ключи, пароли БД, API-ключи, SMTP-пароли) хранятся в .env и не попадают в репозиторий
.env добавлен в .gitignore
Валидация загружаемых файлов: проверка размера (до 2–5 MB), форматов (JPG/PNG/WEBP/PDF), размеров изображений (1920×800 для баннера)
Ограничение количества записей: максимум 5 соцсетей, 5 документов
Защита от CSRF, XSS, SQL-инъекций (встроено в Django ORM и шаблоны)
Использование паролей приложений для SMTP (не основной пароль почты)
HTTPS рекомендуется для продакшена (настраивается в Nginx)

## Лицензия
Проект распространяется под лицензией MIT. Подробности — в файле LICENSE.

#### Автор: Дмитрий Старченко
#### Контакты: Starchenko.Dmitr@mail.ru
#### Репозиторий: github.com/starchenko-dmi/restaurant_booking
#### Дата: Март 2026

## Быстрый старт

### Установка

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/starchenko-dmi/restaurant_booking.git
cd restaurant_booking

# 2. Создайте виртуальное окружение и установите зависимости
poetry install  # или: pip install -r requirements.txt

# 3. Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env: SECRET_KEY, DATABASE_URL, YANDEX_MAPS_API_KEY, EMAIL_* и др.

# 4. Примените миграции
python manage.py migrate

# 5. Создайте суперпользователя
python manage.py createsuperuser

# 6. Соберите статические файлы
python manage.py collectstatic --noinput

# 7. Запустите сервер разработки
python manage.py runserver

Docker Сборка и запуск

# 1. Сборка образа
docker-compose build

# 2. Запуск контейнеров
docker-compose up -d

# 3. Применение миграций в контейнере
docker-compose exec web python manage.py migrate

# 4. Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# 5. Просмотр логов
docker-compose logs -f web

тестирование

# 1. Запустить все тесты с покрытием
coverage run manage.py test

# 2. Посмотреть отчёт в консоли
coverage report

# 3. Сгенерировать HTML-отчёт
coverage html
start htmlcov/index.html  # Windows
