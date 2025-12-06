# bot/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import settings
from backend_client import BackendClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(
    token=settings.telegram_bot_token,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher(storage=MemoryStorage())

# Инициализация BackendClient
backend_client = BackendClient(
    base_url=str(settings.backend_api_url),
    token=settings.backend_api_token
)


async def main():
    try:
        logger.info("Starting bot...")
        
        # Регистрация хендлеров (их нужно импортировать после инициализации)
        from handlers.main_handlers import router
        
        # Подключаем роутеры
        dp.include_router(router)
        
        logger.info("Bot initialized successfully. Starting polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise
    finally:
        # Закрытие соединений
        if hasattr(backend_client, 'close'):
            await backend_client.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())