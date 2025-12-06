# Предпалагаемая архитектура проекта

```
project/
├── bot/
│   ├── handlers/
│   │   ├── balance.py
│   │   ├── qr.py
│   │   ├── rules_bot.py
│   │   ├── rules_school.py
│   │   ├── cyberons.py
│   │   ├── finances.py
│   │   ├── director.py
│   │   └── __init__.py
│   ├── keyboards/
│   │   └── start_menu.py
│   ├── middlewares/
│   │   └── __init__.py
│   ├── bot.py
│   ├── config.py
│   └── __init__.py
├── api/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Основное приложение FastAPI
│   │   ├── config.py            # Настройки
│   │   ├── database.py          # Подключение к БД
│   │   ├── dependencies.py      # Зависимости (DI)
│   │   └── middleware.py        # Middleware (CORS, обработка ошибок)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py              # Авторизация
│   │   ├── users.py             # Пользователи
│   │   ├── finance.py           # Финансы
│   │   ├── admin.py             # Админка (правила)
│   │   ├── messages.py          # Сообщения директору
│   │   └── lessons.py           # Уроки (если нужно)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py              # Схемы пользователей
│   │   ├── finance.py           # Схемы финансов
│   │   ├── messages.py          # Схемы сообщений
│   │   └── admin.py             # Схемы админки
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py              # Базовый класс моделей
│   │   ├── user.py              # Модель пользователя
│   │   ├── finance.py           # Модель финансов
│   │   ├── message.py           # Модель сообщений
│   │   └── admin.py             # Модель настроек
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py              # Сервис авторизации
│   │   ├── users.py             # Сервис пользователей
│   │   ├── finance.py           # Сервис финансов
│   │   ├── messages.py          # Сервис сообщений
│   │   └── alfacrm.py           # Сервис интеграции с AlfaCRM
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── user.py              # CRUD операции для пользователей
│   │   ├── finance.py           # CRUD операции для финансов
│   │   ├── message.py           # CRUD операции для сообщений
│   │   └── admin.py             # CRUD операции для настроек
│   └── alembic/                 # Миграции (позже)
│
├── requirements.txt
└── docker-compose.yml
```

# Пример .env файла
```
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
# Администраторы (через запятую)
TELEGRAM_ADMINS=["205", "132"]

# Database (Postgres)
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5433/testdb

# ID чата или username (например @groupname) для пересылки директору
DIRECTORS_CHAT_ID=your_director_chat_or_id

# Заглушка для QR (можно URL картинки)
PLACEHOLDER_QR_URL=https://via.placeholder.com/300x300?text=QR

# AlphaCRM
ALPHACRM_API_KEY=alphacrm-api-key
```
