import logging

from aiogram import Router, F
from aiogram.types import Message, ErrorEvent, CallbackQuery
from aiogram.filters import ExceptionTypeFilter, CommandStart
from aiogram.fsm.storage.redis import RedisStorage

from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState

from my_tools import DialogManagerKeys

from ..states import Admin, Onboarding
from ..enums import Database, Action
from ..utils.utils import get_middleware_data
from ..queries import add_action
from ..config import Config

from fluentogram import TranslatorHub

router: Router = Router()


def get_current_state(
        dialog_manager: DialogManager, 
        config: Config, 
        user_id: int) -> Onboarding | Admin:

    try:
        current_state = dialog_manager.current_context().state
    except:
        current_state = Onboarding.WELCOME

    return current_state


@router.message(CommandStart())
async def process_start(message: Message, dialog_manager: DialogManager) -> None:

    _, config, user_data = get_middleware_data(dialog_manager)

    log_message = f"Bot is starting for {user_data.id} ({user_data.full_name})"
    logging.warning(log_message)
    await add_action(dialog_manager, Action.START)

    current_state = get_current_state(dialog_manager, config, user_data.id)
    
    await start_dialog(dialog_manager, current_state)


# @router.callback_query(F.data == "flow")
# async def run_flow(callback: CallbackQuery, dialog_manager: DialogManager) -> None:

#     await start_dialog(dialog_manager, Onboarding.WELCOME, show_mode=ShowMode.SEND)


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
        state: Admin,
        mode: StartMode = StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND
        ):

    await dialog_manager.start(
        state=state, 
        mode=mode,
        show_mode=show_mode
        )