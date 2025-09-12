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

async def main() -> None:

    config: Config = load_config()

    start_logging(config.system.time_zone)

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