import asyncio
import signal
import platform
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.config import settings
from config.logging import logger
from database.db import Database
from services.service_manager import ServiceManager
from handlers.admin_handlers import setup_admin_handlers
from handlers.user_handlers import setup_user_handlers

class BotRunner:
    def __init__(self):
        self.bot = None
        self.dp = None
        self.service_manager = None

    async def setup(self):
        try:
            logger.info("Инициализация бота...")
            
            db = Database()
            db._initialize_db()
            
            self.bot = Bot(token=settings.BOT_TOKEN)
            self.dp = Dispatcher(storage=MemoryStorage())
            self.service_manager = ServiceManager(db)

            setup_user_handlers(self.dp, self.service_manager)
            setup_admin_handlers(self.dp, self.service_manager)
            
            logger.info("Компоненты бота успешно инициализированы")
            
        except Exception as e:
            logger.critical(f"Ошибка инициализации: {e}")
            raise

    async def shutdown(self, signal=None):
        logger.info(f"Завершение работы (сигнал: {signal.name if signal else 'manual'})")
        
        try:
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            for task in tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            if self.bot:
                await self.bot.session.close()
                logger.info("Сессия бота закрыта")
                
            if self.service_manager:
                self.service_manager.close()
                
        except Exception as e:
            logger.error(f"Ошибка при завершении работы: {e}")
        finally:
            logger.info("Бот успешно остановлен")

    async def run(self):
        try:
            await self.setup()
            
            if platform.system() != 'Windows':
                loop = asyncio.get_running_loop()
                for sig in (signal.SIGTERM, signal.SIGINT):
                    loop.add_signal_handler(
                        sig, 
                        lambda s=sig: asyncio.create_task(self.shutdown(s)))
            
            logger.info("Бот запущен и готов к работе")
            await self.dp.start_polling(self.bot) # type: ignore
            
        except KeyboardInterrupt:
            logger.info("Получен сигнал KeyboardInterrupt")
        except Exception as e:
            logger.critical(f"Критическая ошибка: {e}")
        finally:
            await self.shutdown()