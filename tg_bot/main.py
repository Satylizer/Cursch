import asyncio
from config.logging import logger
from bot_runner import BotRunner

if __name__ == '__main__':
    runner = BotRunner()
  
    try:
        asyncio.run(runner.run())
    except KeyboardInterrupt:
        logger.info("Бот остановлен по запросу пользователя")
    except Exception as e:
        logger.critical(f"Фатальная ошибка: {e}")