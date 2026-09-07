# 🍽️ Restaurant Booking System

Система бронирования столиков в ресторане на Django с админ-панелью, Яндекс.Картами, настраиваемым контентом и полной валидацией. Автоматизирует процесс бронирования, исключает двойные брони и позволяет управлять контентом сайта без участия разработчика.

[![Tests](https://img.shields.io/badge/tests-62_passed-brightgreen)](#)
[![Coverage](https://img.shields.io/badge/coverage-89.97%25-yellow)](#)
[![Python](https://img.shields.io/badge/python-3.13-blue)](#)
[![Django](https://img.shields.io/badge/django-6.0.3-green)](#)
[![License](https://img.shields.io/badge/license-MIT-orange)](#)

---

## ✨ Функционал

### Для клиентов
- **Онлайн-бронирование**: выбор даты, времени, количества гостей с валидацией доступности в реальном времени
- **Личный кабинет**: просмотр истории бронирований, изменение и отмена заказов
- **Контакты с картой**: интерактивная Яндекс.Карта с меткой ресторана
- **Форма обратной связи**: отправка сообщений на email ресторана через SMTP с валидацией

### Для администраторов
- **Управление контентом без кода**: история, миссия, заголовки страниц через модель `SiteContent`
- **Социальные сети**: 1–5 ссылок с автоматическими иконками Bootstrap Icons (Telegram, WhatsApp, VK, Rutube)
- **Документы в футере**: текстовые страницы или PDF-файлы (до 5 шт.) с кнопкой скачивания
- **Баннер главной**: загрузка изображения с валидацией (1920×800 px, до 2 MB, форматы JPG/PNG/WEBP)
- **Настройки ресторана**: адрес, телефон, email, время работы, координаты карты

### Система
- **Роли пользователей**: обычные пользователи управляют своими данными, менеджеры имеют расширенный доступ через группы Django
- **Валидация на уровне модели**: метод `clean()` в `Reservation` проверяет пересечение бронирований до записи в БД
- **Адаптивный дизайн**: Bootstrap 5.3, корректное отображение на мобильных устройствах
- **Безопасность**: CSRF-токены, защита от XSS, хеширование паролей PBKDF2, секреты в `.env`

---

## 🏗️ Архитектура и технические решения

### Структура приложений Django
```
restaurant_booking/
├── core/      # Контент, настройки, управляемые элементы сайта
├── bookings/  # Логика бронирования, валидация, проверка доступности
└── users/     # Аутентификация, профили, роли пользователей
```

### Ключевые модели и связи

```python
# core/models.py
class RestaurantSettings(models.Model):
    """Единая настройка ресторана (Singleton-паттерн)"""
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    closes_next_day = models.BooleanField(default=False)  # Для заведений после полуночи
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

class SocialLink(models.Model):
    """Ссылки на соцсети с авто-иконками"""
    NETWORK_CHOICES = [('telegram', 'Telegram'), ('whatsapp', 'WhatsApp'), ('vk', 'VK'), ('rutube', 'Rutube'), ('custom', 'Custom')]
    network = models.CharField(max_length=20, choices=NETWORK_CHOICES)
    url = models.URLField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    @property
    def icon_class(self):
        """Автоматическая иконка Bootstrap Icons"""
        return f"bi bi-{self.network}" if self.network != 'custom' else 'bi bi-share'

class FooterDocument(models.Model):
    """Документы в футере (текст или PDF)"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='documents/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

# bookings/models.py
class Table(models.Model):
    """Столики ресторана"""
    number = models.CharField(max_length=10, unique=True)
    capacity = models.PositiveIntegerField()  # Вместимость
    is_active = models.BooleanField(default=True)

class Reservation(models.Model):
    """Бронирование столика"""
    STATUS_CHOICES = [('pending', 'Ожидает'), ('confirmed', 'Подтверждено'), ('cancelled', 'Отменено')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    end_time = models.TimeField(editable=False)  # Рассчитывается автоматически
    guests_count = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def clean(self):
        """Валидация: проверка вместимости и пересечения бронирований"""
        if self.guests_count > self.table.capacity:
            raise ValidationError("Превышена вместимость столика")
        # Проверка на пересечение временных интервалов
        overlapping = Reservation.objects.filter(
            table=self.table, date=self.date, status__in=["confirmed", "pending"]
        ).exclude(pk=self.pk).filter(
            Q(time__lt=self.end_time, end_time__gt=self.time)
        )
        if overlapping.exists():
            raise ValidationError("Столик уже забронирован")
    
    def save(self, *args, **kwargs):
        """Автоматический расчёт end_time (бронь на 2 часа)"""
        if self.time:
            from datetime import timedelta, datetime
            start = datetime.combine(self.date, self.time)
            self.end_time = (start + timedelta(hours=2)).time()
        super().save(*args, **kwargs)
```

### Связи между моделями
- `Reservation.user` → `CustomUser` (ForeignKey, один ко многим)
- `Reservation.table` → `Table` (ForeignKey, один ко многим)
- `SocialLink`, `FooterDocument`, `HeroImage` привязаны к `SiteContent` через контекст-процессоры для отображения во всех шаблонах

### Ключевые технические решения
1. **Валидация на уровне модели**: метод `clean()` гарантирует целостность данных даже при прямом доступе к БД
2. **Контекст-процессоры**: `footer_data` передаёт соцсети и документы во все шаблоны без дублирования кода
3. **Гибкое время работы**: поле `closes_next_day` поддерживает заведения, работающие после полуночи
4. **Роли через группы Django**: `@user_passes_test(lambda u: u.groups.filter(name='managers').exists())` для гибкого контроля доступа
5. **SMTP через переменные окружения**: пароли и ключи не попадают в репозиторий

---

## 🛠️ Стек технологий

- **Бэкенд**: Python 3.13, Django 6.0.3
- **База данных**: PostgreSQL 14+ (продакшен), SQLite (разработка)
- **Фронтенд**: Bootstrap 5.3, Bootstrap Icons, jQuery, Яндекс.Карты API
- **Контейнеризация**: Docker, Docker Compose
- **Тестирование**: Django TestCase, coverage.py (покрытие 89.97%)
- **Качество кода**: black, isort, flake8 (PEP 8)
- **Управление зависимостями**: Poetry / pip + requirements.txt
- **Деплой**: Gunicorn, Nginx, Docker Hub

---

## 🚀 Быстрый старт

### Требования
- Python 3.13+
- PostgreSQL 14+ (или Docker для контейнеризации)
- Poetry (рекомендуется) или pip

### Установка

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/starchenko-dmi/RestaurantBooking.git
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
```

Откройте `http://127.0.0.1:8000/` — сайт готов к работе!

### Запуск с Docker (PostgreSQL в контейнере)

```bash
# 1. Запустите контейнеры
docker-compose up -d

# 2. Примените миграции в контейнере
docker-compose exec web python manage.py migrate

# 3. Создайте суперпользователя
docker-compose exec web python manage.py createsuperuser

# 4. Сайт доступен на http://127.0.0.1:8000/
```

---

## ⚙️ Конфигурация (.env.example)

```env
# Django
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# База данных
DATABASE_URL=postgres://user:pass@localhost:5432/restaurant_db

# Яндекс.Карты
YANDEX_MAPS_API_KEY=your-yandex-maps-api-key

# Email (SMTP Яндекс для формы обратной связи)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@yandex.ru
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@yandex.ru

# Медиа-файлы
MEDIA_ROOT=media/
MEDIA_URL=/media/
```

---

## 📁 Структура проекта

```
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
├── .env.example          # Шаблон переменных окружения
├── .gitignore           # Исключения для Git
├── requirements.txt     # Зависимости для продакшена
├── pyproject.toml       # Конфигурация Poetry
├── Dockerfile           # Образ для продакшена
├── docker-compose.yml   # Оркестрация контейнеров
└── manage.py            # Точка входа Django
```

---

## 🌐 API и эндпоинты

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| GET | `/` | Главная страница | Все |
| GET | `/about/` | О ресторане | Все |
| GET | `/contacts/` | Контакты с картой и формой | Все |
| POST | `/contacts/` | Отправка сообщения (форма обратной связи) | Все |
| GET | `/bookings/create/` | Форма бронирования | Авторизованные |
| POST | `/bookings/create/` | Создание бронирования | Авторизованные |
| GET | `/profile/` | Личный кабинет с историей | Авторизованные |
| GET | `/document/<slug>/` | Просмотр документа (оферта, политика) | Все |
| GET | `/admin/` | Панель управления | Суперпользователи |

---

## 🧪 Тестирование

```bash
# Запустить все тесты с покрытием
coverage run manage.py test

# Посмотреть отчёт в консоли
coverage report

# Сгенерировать HTML-отчёт
coverage html
start htmlcov/index.html  # Windows
```

**Ожидаемый результат:**
```
Ran 62 tests in 51.847s
OK
Name                     Stmts   Miss   Cover
---------------------------------------------
TOTAL                      997    100    89.97%
```

---

## 🔐 Безопасность

- Все чувствительные данные (секретные ключи, пароли БД, API-ключи, SMTP-пароли) хранятся в `.env` и не попадают в репозиторий
- `.env` добавлен в `.gitignore`
- Валидация загружаемых файлов: проверка размера (до 2–5 MB), форматов (JPG/PNG/WEBP/PDF), размеров изображений (1920×800 для баннера)
- Ограничение количества записей: максимум 5 соцсетей, 5 документов
- Защита от CSRF, XSS, SQL-инъекций (встроено в Django ORM и шаблоны)
- Использование паролей приложений для SMTP (не основной пароль почты)
- Хеширование паролей алгоритмом PBKDF2 с солью

---

## 📊 Метрики качества

| Метрика | Значение |
|---------|----------|
| Тестов | 62 ✅ |
| Покрытие кода | 89.97% 🎯 |
| Линтеры | flake8 (0 ошибок), black, isort |
| Статус сборки | ✅ Проходит |
| Статус тестов | ✅ Все проходят |
| Форматирование | ✅ Код отформатирован по PEP 8 |

---

## 📸 Скриншоты

### Главная страница
![Главная страница](https://via.placeholder.com/800x400?text=Главная+страница+с+баннером+и+услугами)

### Форма бронирования
![Бронирование](https://via.placeholder.com/800x400?text=Форма+бронирования+с+валидацией)

### Админка — управление контентом
![Админка](https://via.placeholder.com/800x400?text=Админка+Django+с+управлением+контентом)

### Мобильная версия
![Мобильная версия](https://via.placeholder.com/400x800?text=Адаптивный+дизайн+Bootstrap+5)

---

## 🤝 Вклад в проект

1.  Создайте форк репозитория
2.  Создайте ветку для фичи: `git checkout -b feature/amazing-feature`
3.  Внесите изменения и отформатируйте код: `black . && isort .`
4.  Убедитесь, что тесты проходят: `coverage run manage.py test && coverage report`
5.  Закоммитьте изменения: `git commit -m 'feat: добавлена потрясающая фича'`
6.  Отправьте пул-реквест

---

## 📄 Лицензия

Проект распространяется под лицензией MIT. Подробности — в файле `LICENSE`.

---

## 👤 Автор

**Дмитрий Старченко**  
📧 [Starchenko.Dmitr@mail.ru](mailto:Starchenko.Dmitr@mail.ru)  
🔗 [GitHub](https://github.com/starchenko-dmi)  
🎓 Дипломный проект, Март 2026

---

> 💡 **Совет**: Для продакшена установите `DEBUG=False`, настройте HTTPS через Nginx и используйте Gunicorn вместо `runserver`.
