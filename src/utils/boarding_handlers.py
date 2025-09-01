import os
import asyncio
import logging

import asyncio
import aiofiles

from aiogram.types import CallbackQuery, Message
from aiogram.enums import ContentType

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import MessageInput, ManagedTextInput, TextInput
from aiogram_dialog.api.entities import MediaAttachment, MediaId

from .utils import get_middleware_data
from my_tools import get_datetime_now, DateTimeKeys

from ..states import Onboarding
from .utils import get_middleware_data, determine_russian_name_gender
from .face_handlers import analyze_face_in_image
from ..queries import add_action

from my_tools import get_datetime_now, DateTimeKeys


MAX_BYTES = 10 * 1024 * 1024


async def go_back(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    current_state = dialog_manager.current_context().state

    await add_action(dialog_manager)
    
    match current_state:
        case Onboarding.STEP_1:
            await dialog_manager.switch_to(Onboarding.NO_PHOTO)
        
        case Onboarding.NO_PHOTO:
            await dialog_manager.switch_to(Onboarding.SOMETHING_ELSE)

        case Onboarding.PHOTO:
            await dialog_manager.switch_to(Onboarding.SOMETHING_ELSE)

        case _:
            await dialog_manager.back()


async def go_next(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    await add_action(dialog_manager)
    await dialog_manager.next()


# Callback handlers for the buttons
async def on_approve(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    await add_action(dialog_manager)
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

    _, _, user_data = get_middleware_data(dialog_manager)
    
    # Determine gender from the full name
    gender = determine_russian_name_gender(text)
    dialog_manager.dialog_data["gender"] = gender

    await write_txt_file(text, user_data.id)

    await add_action(dialog_manager)
    await dialog_manager.next()


async def error_name_handler(
        message: Message, 
        widget: ManagedTextInput, 
        dialog_manager: DialogManager, 
        error: ValueError):
        
    await message.answer(
        text='Вы ввели некорректное имя.'
    )

    await asyncio.sleep(1)


async def write_txt_file(text: str, user_id: int, widget_id: str = "0"):

    date: str = get_datetime_now(DateTimeKeys.DEFAULT)

    # Save text content to file asynchronously
    file_path = f"media/{user_id}/onboarding/{widget_id}_text_{date}.txt"
    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
        await f.write(text)


async def text_input_handler(
        message: Message, 
        widget: ManagedTextInput, 
        dialog_manager: DialogManager, 
        text: str) -> None:

    _, _, user_data = get_middleware_data(dialog_manager)

    await add_action(dialog_manager)
    await write_txt_file(text, user_data.id, widget.widget.widget_id)

    await dialog_manager.next()


def create_media_input(input_id: int) -> MessageInput:
    """
    Create a media input for a specific window.
    """
    return MessageInput(
        func=handle_voice_and_video_note,
        content_types= [ContentType.VOICE, ContentType.VIDEO_NOTE],
        id=f"{input_id}"
    )


def create_text_input(input_id: int) -> TextInput:
    """
    Create a text input for a specific window.
    """
    return TextInput(
        id=f"{input_id}",
        on_success=text_input_handler
    )


def create_photo_input(input_id: int) -> MessageInput:
    """
    Create a photo input.
    """
    return MessageInput(
        func=handle_photo,
        content_types= ContentType.ANY
    )    


# Хэндлер, который сработает, если пользователь отправил вообще не текст
async def handle_voice_and_video_note(message: Message, widget: MessageInput, dialog_manager: DialogManager):

    bot, _, user_data = get_middleware_data(dialog_manager)
    await add_action(dialog_manager)

    date: str = get_datetime_now(DateTimeKeys.DEFAULT)
    widget_id = widget.widget_id

    if message.voice:
        if message.voice.file_size <= MAX_BYTES:
            await bot.download(
                file=message.voice.file_id, 
                destination=f"media/{user_data.id}/onboarding/{widget_id}_voice_{date}.ogg"
                )
            await dialog_manager.next()

        else:
            await message.answer("⚠️ Голосовое слишком большое (>10 МБ). Отправьте более короткую запись.")
            await asyncio.sleep(1)
            return

    elif message.video_note:
        if message.video_note.file_size <= MAX_BYTES:
            await bot.download(
                file=message.video_note.file_id, 
                destination=f"media/{user_data.id}/onboarding/{widget_id}_video_note_{date}.mp4"
                )
            await dialog_manager.next()
        
        else:
            await message.answer("⚠️ Кружочек слишком большой (>10 МБ). Отправьте более короткий.")
            await asyncio.sleep(1)
            return
        
    else:
        await message.answer(text='❗Это должен быть текст, голосовое или кружочек')
        await asyncio.sleep(1)


async def photo_getter(
    dialog_manager: DialogManager,
    **kwargs):

    photo_file_id = dialog_manager.dialog_data.get('photo_file_id')

    photo = MediaAttachment(
        type=ContentType.PHOTO, 
        file_id=MediaId(photo_file_id))

    return {'photo': photo}


async def download_photo(
    message: Message,
    dialog_manager: DialogManager) -> None:

    bot, _, user_data = get_middleware_data(dialog_manager)

    dialog_manager.dialog_data["photo"] = True

    date: str = get_datetime_now(DateTimeKeys.DEFAULT)
    await bot.download(
        file=message.photo[-1].file_id, 
        destination=f"media/{user_data.id}/onboarding/4_profile_{date}.jpg")


async def confirm_photo_handler(
        callback: CallbackQuery, 
        button: Button, 
        dialog_manager: DialogManager) -> None:
    """
    Handler for the "Yes" button that confirms using the current photo.
    This should be called instead of handle_photo for button clicks.
    """

    await download_photo(callback.message, dialog_manager)
    await add_action(dialog_manager)
    
    await callback.answer("✅ Фотография успешно загружена")
    await asyncio.sleep(1)
    await dialog_manager.switch_to(Onboarding.STEP_1)


async def handle_photo(
    message: Message, 
    widget: MessageInput, 
    dialog_manager: DialogManager):


    bot, _, used_data = get_middleware_data(dialog_manager)

    if not message.photo:
        await message.answer(text='❗Это должна быть фотография')
        await asyncio.sleep(1)
        return

    success, error_message, _ = await analyze_face_in_image(
        bot, message.photo[-1].file_id, used_data.id)
    
    if not success:
        await message.answer(text=error_message)
        await asyncio.sleep(1)
        return

    await add_action(dialog_manager)

    await download_photo(message, dialog_manager)

    await message.answer(text='✅ Фотография успешно загружена')
    await asyncio.sleep(1)

    await dialog_manager.switch_to(Onboarding.STEP_1)


async def handle_profile(
    callback: CallbackQuery, 
    button: Button, 
    dialog_manager: DialogManager):

    bot, _, user_data = get_middleware_data(dialog_manager)

    # Получаем фотографии профиля
    photos = await bot.get_user_profile_photos(user_id=user_data.id)

    if photos.total_count == 0:
        await dialog_manager.switch_to(Onboarding.NO_PHOTO)
        return

    best_photo = None
    best_face_ratio = 0

    # Перебираем все фотографии профиля для поиска лучшей
    for photo in photos.photos:
        success, _, face_ratio = await analyze_face_in_image(bot, photo[-1].file_id, user_data.id)
        
        if success and face_ratio and face_ratio > best_face_ratio:
            best_face_ratio = face_ratio
            best_photo = photo[-1]

    if best_photo is None:
        # Если не найдено подходящее фото, переходим к загрузке нового
        await dialog_manager.switch_to(Onboarding.NO_PHOTO)
        return

    
    dialog_manager.dialog_data["photo_file_id"] = best_photo.file_id
    await dialog_manager.switch_to(Onboarding.PHOTO)
    