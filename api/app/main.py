# api/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.database import engine, Base
from app.middleware import LoggingMiddleware, ErrorHandlingMiddleware

# Импортируем роутеры
from routers import (
    auth,
    users,
    finance,
    admin,
    messages
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Создание приложения
app = FastAPI(
    title="KIBERone Backend API",
    description="Backend для Telegram бота KIBERone с интеграцией AlfaCRM",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(finance.router, prefix="/finance", tags=["Finance"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])


@app.on_event("startup")
async def startup():
    """Действия при запуске приложения"""
    logger.info("Starting KIBERone Backend API...")
    
    # Создаем таблицы в БД
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully")


@app.on_event("shutdown")
async def shutdown():
    """Действия при остановке приложения"""
    logger.info("Shutting down KIBERone Backend API...")
    await engine.dispose()


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "KIBERone Backend API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else None
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {
        "status": "healthy",
        "service": "kiberone-backend",
        "timestamp": "2024-01-01T00:00:00Z"  # TODO: добавить реальное время
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
