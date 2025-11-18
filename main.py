"""
AKB Cargo Bot - Main File
Asosiy bot fayli - barcha handlerlarni bog'laydi
"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN, ensure_directories
from database.db_manager import DatabaseManager

# Handlerlarni import qilish
from handlers import auth, user, admin, search
from utils import exel_utils

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Bot ishga tushganda"""
    logger.info("Bot is starting...")
    
    # Database ni initialize qilish
    db = DatabaseManager()
    await db.init_db()
    
    logger.info("Database initialized")
    logger.info("Bot started successfully!")


async def on_shutdown(bot: Bot):
    """Bot to'xtaganda"""
    logger.info("Bot is shutting down...")
    await bot.session.close()


async def main():
    """Asosiy funksiya"""
    # Papkalarni yaratish
    ensure_directories()
    
    # Logging sozlash
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/bot.log', encoding='utf-8')
        ]
    )
    
    # Bot va Dispatcher yaratish
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Handlerlarni ro'yxatdan o'tkazish (tartib muhim!)
    dp.include_router(admin.router)  # Admin birinchi (callback handlerlar uchun)
    dp.include_router(auth.router)   # Auth ikkinchi (start va ro'yxat)
    dp.include_router(exel_utils.router)   # Exel import handlerlari
    dp.include_router(user.router)   # User (umumiy handlerlar)
    dp.include_router(search.router) # Qidiruv uchinchi
    
    # Startup/Shutdown callbacklari
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Eski updatelarni o'chirish
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("Starting polling...")
    
    # Polling ni boshlash
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")