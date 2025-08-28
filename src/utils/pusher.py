from typing import TYPE_CHECKING

import logging

import asyncio

from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.storage.redis import RedisStorage

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button


from my_tools import get_users

from ..custom_types import UserNotify
from ..enums import Database

from ..utils.utils import get_middleware_data

from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


async def run_pusher(
        callback: CallbackQuery, 
        button: Button, 
        dialog_manager: DialogManager
        ):
    
    bot, config, _ = get_middleware_data(dialog_manager)
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
    temp: RedisStorage = dialog_manager.middleware_data.get(Database.TEMP)

    now: datetime = datetime.now(ZoneInfo(config.system.time_zone))
    current_date = now.date().isoformat()

    value_counter = await temp.redis.incr(f"{config.bot.id}:counter")
    push_text = await temp.redis.get(f"{config.bot.id}_push_{value_counter}")
    
    
    known_users: list[int] = await get_users(users, []) # [414215176, 79670669769] # 

    for user in known_users:

        try:
            if value_counter < 8:
                await bot.send_message(
                        chat_id=user, 
                        text=push_text.decode("utf-8")
                        )
                
            else:

                start_btn = InlineKeyboardButton(
                    text=i18n.offboarding.ready_btn(),
                    callback_data="flow"
                )

                await bot.send_message(
                        chat_id=user, 
                        text=i18n.offboarding.bye_message(),
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[start_btn]]),
                        )
            
            status = True
            logging.warning(f"NOTIFY MESSAGE for {user} on {current_date}")

        except Exception as e:
            
            status = False
            logging.warning(f"Can't send notify message for {user} on {current_date}")
            logging.exception(f"{e}")

        finally:

            user_notify: UserNotify = UserNotify(id=user, status=status)
            await temp.redis.lpush("notified_list", user_notify.model_dump_json(indent=4))
            await asyncio.sleep(1)