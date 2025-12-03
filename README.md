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
│   ├── main.py
│   ├── routers/
│   │   ├── admin.py
│   │   ├── crm.py
│   │   └── __init__.py
│   └── __init__.py
├── db/
│   ├── models.py
│   ├── session.py
│   ├── crud.py
│   └── __init__.py
├── migrations/            # alembic
└── run.py
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
