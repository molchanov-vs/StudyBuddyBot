import asyncio
import time
import logging
import subprocess
import os

from aiogram import Bot, Dispatcher
import redis.asyncio as redis

from src.config import load_config, Config
from src.setups import setup_bot, setup_dispathcer

from fluentogram import TranslatorHub
from src.utils.i18n import create_translator_hub

from src.utils.time_handler import start_logging
from src.utils.utils import remove_logs

from scripts.get_locales import update_locales

logger = logging.getLogger(__name__)


async def flush_redis_databases(config: Config) -> None:
    """Flush all Redis databases in development mode."""
    if os.getenv('DEVELOPMENT', 'false').lower() == 'true':
        try:
            # Connect to Redis
            redis_client = redis.Redis.from_url(config.redis.fsm, decode_responses=True)
            
            # Flush all databases (0, 1, 2, 3)
            for db_num in range(4):
                await redis_client.select(db_num)
                await redis_client.flushdb()
                logger.info(f"Flushed Redis database {db_num}")
            
            await redis_client.aclose()
            logger.warning("All Redis databases flushed in development mode!")
            
        except Exception as e:
            logger.error(f"Failed to flush Redis databases: {e}")


async def main() -> None:

    config: Config = load_config()

    start_logging(config.system.time_zone)

    # Flush Redis databases in development mode
    await flush_redis_databases(config)

    bot: Bot = await setup_bot(config)
    dp: Dispatcher = await setup_dispathcer(config=config)
    translator_hub: TranslatorHub = create_translator_hub()

    remove_logs()

    try:
        print(f"{config.bot.name} is running...")
        await dp.start_polling(
            bot,
            config=config,
            _translator_hub=translator_hub
            )
        
    except Exception as e:
        logger.exception(e)

    finally:
        await bot.session.close()


if __name__ == "__main__":

    # Force locale update if environment variable is set
    force_update = os.getenv('FORCE_LOCALE_UPDATE', 'false').lower() == 'true'
    
    try:
        update_locales()
        subprocess.run(["fluentogram", "-f", "src/locales/ru/txt.ftl", "-o", "src/locales/stub.pyi"])
        print("\nLocales has been updated\n")
    except Exception as e:
        print(f"Warning: Could not update locales: {e}")
        print("Continuing without locale update...")

    asyncio.run(main())