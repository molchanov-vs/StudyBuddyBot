from aiogram import Bot, Dispatcher, Router

from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from aiogram_dialog import setup_dialogs

from src.handlers.start import router as start_router
from src.dialogs.admin import dialog as admin_dialog
from src.dialogs.onboarding import dialog as onboarding_dialog

from src.config import Config

from src.middlewares.redis_storage import RedisStorageMiddleware
from src.middlewares.i18n import TranslatorRunnerMiddleware

from src.enums import Database


router = Router()
router.include_routers(
    start_router,
    onboarding_dialog,
    admin_dialog
)

async def setup_bot(config: Config) -> Bot:

    bot: Bot = Bot(
        token=config.bot.token, 
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML, 
            link_preview_is_disabled=True
            )) 

    main_menu_commands = [
        BotCommand(command='/start', description='🚀 Start')
        ]
    await bot.set_my_commands(main_menu_commands)
    await bot.delete_webhook(drop_pending_updates=True)

    return bot


async def setup_dispathcer(config: Config) -> Dispatcher:

    fsm: RedisStorage = RedisStorage.from_url(
        url=config.redis.fsm, 
        connection_kwargs={"client_name": Database.FSM.value},
        key_builder=DefaultKeyBuilder(
            with_bot_id=True,
            with_destiny=True
            ))
    
    users: RedisStorage = RedisStorage.from_url(
        url=config.redis.users, 
        connection_kwargs={"client_name": Database.USERS.value})
    
    temp: RedisStorage = RedisStorage.from_url(
        url=config.redis.temp, 
        connection_kwargs={"client_name": Database.TEMP.value})
    
    dp: Dispatcher = Dispatcher(storage=fsm)
    
    dp.update.middleware.register(RedisStorageMiddleware(storage=fsm, db_name=Database.FSM))
    dp.update.middleware.register(RedisStorageMiddleware(storage=users, db_name=Database.USERS))
    dp.update.middleware.register(RedisStorageMiddleware(storage=temp, db_name=Database.TEMP))

    dp.update.middleware(TranslatorRunnerMiddleware())

    dp.include_router(router)

    setup_dialogs(dp)
    return dp