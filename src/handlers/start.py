from typing import Any

import logging

from aiogram import Router, F
from aiogram.types import Message, ErrorEvent, CallbackQuery
from aiogram.filters import ExceptionTypeFilter, CommandStart
from aiogram.fsm.storage.redis import RedisStorage

from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState

from my_tools import DialogManagerKeys

from ..states import Admin, Onboarding, Flow
from ..enums import Database, Action, RedisKeys
from ..utils.utils import get_middleware_data
from ..queries import add_action
from ..config import Config

from fluentogram import TranslatorHub

router: Router = Router()


def get_current_state(
        dialog_manager: DialogManager, 
        config: Config, 
        user_id: int) -> Onboarding | Admin:

    if user_id in config.superadmins.ids:
        return Admin.MAIN

    try:
        current_state = dialog_manager.current_context().state

    except:
        current_state = Flow.MENU

    return current_state


WARNING_MESSAGE = """
<b>❗Похоже у вас нет доступа к боту. Пожалуйста, обратитесь к <a href="https://t.me/anastasia_ilu">Насте</a></b>
"""

@router.message(CommandStart())
async def process_start(message: Message, dialog_manager: DialogManager) -> None:

    bot, config, user_data = get_middleware_data(dialog_manager)

    log_message = f"Bot is starting for {user_data.id} ({user_data.full_name})"
    logging.warning(log_message)

    users_storage: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)

    if await users_storage.redis.sismember(RedisKeys.KNOWN_USERS, user_data.id):
    
        await add_action(dialog_manager, Action.START)

        if user_data.id in config.superadmins.ids:
            await start_dialog(dialog_manager, Admin.MAIN)
        else:
            await start_dialog(dialog_manager, Flow.MENU)

    else:
        await bot.send_message(chat_id=user_data.id, text=WARNING_MESSAGE)


@router.message(F.forward_from)
async def process_message(message: Message, dialog_manager: DialogManager) -> None:

    bot, config, user_data = get_middleware_data(dialog_manager)
    users_storage: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)

    if message.from_user.id in config.admins.ids:

        await users_storage.redis.sadd(RedisKeys.KNOWN_USERS, message.forward_from.id)
        user = f"{message.forward_from.first_name} {message.forward_from.last_name} ({message.forward_from.id})"
        await bot.send_message(
            chat_id=user_data.id, 
            text=f"Пользователь {user} добавлен!")

        await bot.send_message(chat_id=message.forward_from.id, text="Теперь вы можете использовать бот!\nПожалуйста, нажмите /start")
        logging.warning(f"User {user} added")

    else:
        await bot.send_message(chat_id=user_data.id, text=WARNING_MESSAGE)


@router.callback_query(F.data == "flow")
async def run_flow(callback: CallbackQuery, dialog_manager: DialogManager) -> None:

    _, config, user_data = get_middleware_data(dialog_manager)
    current_state = get_current_state(dialog_manager, config, user_data.id)
    await start_dialog(dialog_manager, current_state, show_mode=ShowMode.SEND)


@router.errors(ExceptionTypeFilter(UnknownIntent))
async def on_unknown_intent(event: ErrorEvent, dialog_manager: DialogManager):
    """Handle UnknownIntent Error and start a new dialog."""
    await handle_error_and_restart(event, dialog_manager, "UnknownIntent")


@router.errors(ExceptionTypeFilter(UnknownState))
async def on_unknown_state(event: ErrorEvent, dialog_manager: DialogManager):
    """Handle UnknownState Error and start a new dialog."""
    await handle_error_and_restart(event, dialog_manager, "UnknownState")


async def handle_error_and_restart(event: ErrorEvent, dialog_manager: DialogManager, error_type: str):
    """Common logic for handling errors and restarting the dialog."""

    _, config, user_data = get_middleware_data(dialog_manager)

    logging.error(f"{error_type} Error for {user_data.id} ({user_data.full_name}). Restarting dialog: %s", event.exception)

    # Update middleware data with Redis storage instances
    dialog_manager.middleware_data[Database.USERS.value] = RedisStorage.from_url(url=config.redis.users)
    dialog_manager.middleware_data[Database.TEMP.value] = RedisStorage.from_url(url=config.redis.temp)

    # Set up the translator for the user's language
    hub: TranslatorHub = dialog_manager.middleware_data.get(DialogManagerKeys.TRANSLATOR_HUB)
    dialog_manager.middleware_data['i18n'] = hub.get_translator_by_locale(locale=user_data.language_code)

    # Restart the dialog
    await add_action(dialog_manager, Action.RESTART)
    current_state = get_current_state(dialog_manager, config, user_data.id)
    
    await start_dialog(dialog_manager, current_state)


async def start_dialog(
        dialog_manager: DialogManager, 
        state: Onboarding,
        start_data: dict[str, Any] | None = None,
        mode: StartMode = StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND
        ):

    await dialog_manager.start(
        state=state, 
        mode=mode,
        show_mode=show_mode,
        data=start_data
        )