from typing import Any, TYPE_CHECKING

import os
import asyncio
import logging

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.state import State


from ..enums import Database, Action
from ..states import Onboarding
from ..custom_types import UserOnboarding, UserOffboarding
from .utils import get_current_state, get_middleware_data
from .face_handlers import analyze_face_in_image
from ..queries import add_action

from my_tools import get_datetime_now, DateTimeKeys

from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


async def get_numbers(**kwargs):
    nums = [
        ("1️⃣", '1'),
        ("2️⃣", '2'),
        ("3️⃣", '3'),
        ("4️⃣", '4'),
        ("5️⃣", '5'),
    ]
    return {
        "nums": nums,
        "count": len(nums),
    }


async def get_last_user_on(users: RedisStorage, user_id: int) -> UserOnboarding:

    user_onboarding_raw = await users.redis.lrange(f"{user_id}_on", 0, -1)
    if user_onboarding_raw:
        return UserOnboarding.model_validate_json(user_onboarding_raw[0])

    return UserOnboarding()


async def get_last_user_off(users: RedisStorage, user_id: int) -> UserOffboarding:

    user_offboarding_raw = await users.redis.lrange(f"{user_id}_off", 0, -1)
    if user_offboarding_raw:
        return UserOffboarding.model_validate_json(user_offboarding_raw[0])
    
    return UserOffboarding()


# Callback handlers for the buttons
async def on_approve(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)

    user_oboarding: UserOnboarding = UserOnboarding(approve=True)
    await users.redis.lpush(f"{callback.from_user.id}_on", user_oboarding.model_dump_json(indent=4))
    await add_action(dialog_manager, Action.ONBOARDING)

    os.makedirs(f"media/{callback.from_user.id}/onboarding", exist_ok=True)

    await dialog_manager.next()


def name_check(text: str) -> str:
    if not text:
        raise ValueError
    
    # Check if text contains exactly two words
    words = text.strip().split()
    if len(words) != 2:
        logging.error(f"Name must contain exactly two words: {text}")
        raise ValueError
    
    # Check if each word contains Russian characters and is more than one symbol
    russian_chars = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
    
    # Validate that each word contains at least some Russian characters and is more than one symbol
    for word in words:
        if len(word) <= 1:
            logging.error(f"Each word must be more than one symbol: {text}")
            raise ValueError
        
        word_chars = set(word)
        if not word_chars.intersection(russian_chars):
            logging.error(f"Name must contain only Russian characters: {text}")
            raise ValueError
    
    return text

# Хэндлер, который сработает, если пользователь ввел корректный возраст
async def correct_name_handler(
        message: Message, 
        widget: ManagedTextInput, 
        dialog_manager: DialogManager, 
        text: str) -> None:
    
    users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
    user_oboarding: UserOnboarding = await get_last_user_on(users, message.from_user.id)

    user_oboarding.name = text
    dialog_manager.dialog_data["name"] = text.split()[0]

    await add_action(dialog_manager, Action.ONBOARDING)
    await users.redis.lpush(f"{message.from_user.id}_on", user_oboarding.model_dump_json(indent=4))
    await dialog_manager.next()


async def error_name_handler(
        message: Message, 
        widget: ManagedTextInput, 
        dialog_manager: DialogManager, 
        error: ValueError):
        
    await message.answer(
        text='Вы ввели некорректное имя. Попробуйте еще раз'
    )

    await asyncio.sleep(1)


async def text_input_handler(
        message: Message, 
        widget: ManagedTextInput, 
        dialog_manager: DialogManager, 
        text: str) -> None:

    await dialog_manager.next()


async def handle_profile(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    bot, _, user_data = get_middleware_data(dialog_manager)

    # Получаем фотографии профиля
    photos = await bot.get_user_profile_photos(user_id=user_data.id)

    if photos.total_count == 0:
        await dialog_manager.switch_to(Onboarding.NO_PHOTO)
        return

    best_photo = None
    best_face_ratio = 0
    # date: str = get_datetime_now(DateTimeKeys.DEFAULT)

    # Перебираем все фотографии профиля для поиска лучшей
    for photo in photos.photos:
        success, _, face_ratio = await analyze_face_in_image(bot, photo[-1].file_id)
        
        if success and face_ratio and face_ratio > best_face_ratio:
            best_face_ratio = face_ratio
            best_photo = photo[-1]

    if best_photo is None:
        # Если не найдено подходящее фото, переходим к загрузке нового
        await dialog_manager.switch_to(Onboarding.NO_PHOTO)
        return

    
    dialog_manager.dialog_data["photo_file_id"] = best_photo.file_id
    await dialog_manager.switch_to(Onboarding.PHOTO)

    # # Сохраняем лучшую фотографию
    # await bot.download(
    #     file=best_photo.file_id,
    #     destination=f"media/{user_data.id}/onboarding/profile_{date}.jpg"
    # )

    # await dialog_manager.next()
    