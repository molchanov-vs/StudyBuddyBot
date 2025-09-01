from typing import TYPE_CHECKING

import asyncio
import aiofiles


from aiogram.types import Message
from aiogram.enums import ContentType
from aiogram.fsm.storage.redis import RedisStorage

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Row, Next
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.input import TextInput, MessageInput, ManagedTextInput
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.media import DynamicMedia


from my_tools import get_datetime_now, DateTimeKeys

from ..utils.boarding_handlers import on_approve, on_next, on_back, \
    name_check, correct_name_handler, error_name_handler, \
        handle_profile, confirm_photo_handler, handle_photo

from ..utils.utils import get_middleware_data, load_locales

from ..states import Onboarding

from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


MAX_BYTES = 10 * 1024 * 1024


async def photo_getter(
    dialog_manager: DialogManager,
    **kwargs):

    photo_file_id = dialog_manager.dialog_data.get('photo_file_id')

    photo = MediaAttachment(
        type=ContentType.PHOTO, 
        file_id=MediaId(photo_file_id))

    return {'photo': photo}



async def dialog_get_data(
        i18n: TranslatorRunner,
        users: RedisStorage,
        dialog_manager: DialogManager,
        **kwargs):
    
    _, _, user_data = get_middleware_data(dialog_manager)
    
    data: dict[str, str] = load_locales(i18n, dialog_manager)

    nav = dialog_manager.dialog_data.get("nav", {})
    if nav and nav.can_go_next():
        data["on_next_btn"] = True

    return data


# Хэндлер, который сработает, если пользователь отправил вообще не текст
async def handle_voice_and_video_note(message: Message, widget: MessageInput, dialog_manager: DialogManager):

    bot, _, user_data = get_middleware_data(dialog_manager)

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

async def text_input_handler(
        message: Message, 
        widget: ManagedTextInput, 
        dialog_manager: DialogManager, 
        text: str) -> None:

    _, _, user_data = get_middleware_data(dialog_manager)
    date: str = get_datetime_now(DateTimeKeys.DEFAULT)

    widget_id = widget.widget.widget_id

    # Save text content to file asynchronously
    file_path = f"media/{user_data.id}/onboarding/{widget_id}_text_{date}.txt"
    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
        await f.write(text)

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
        content_types= ContentType.PHOTO
    )


BACK_NEXT_BTNS = Row(
    Button(Format("{back_btn}"), id="back_btn_id", on_click=on_back),
    # Button(Format("{next_btn}"), id="next_btn_id", on_click=on_next, when="on_next_btn"),
)


# Dialog with windows using Format for localization
dialog = Dialog(

    Window(
        Format("{welcome}"),
        Next(Format("{super_btn}"), id="super_btn_id"),
        state=Onboarding.WELCOME
    ),

    Window(
        Format("{preonboarding}"),
        Button(Format("{approve_btn}"), id="approve", on_click=on_approve),
        state=Onboarding.PREONBOARDING
    ),

    Window(
        Format("{name}"),
        Button(Format("{next_btn}"), id="next_btn_id", on_click=on_next, when="on_next_btn"),
        TextInput(
            id='name_input',
            type_factory=name_check,
            on_success=correct_name_handler,
            on_error=error_name_handler,
        ),
        state=Onboarding.NAME
    ),

    Window(
        Format("{important_today}"),
        BACK_NEXT_BTNS,
        create_text_input(input_id=1),
        create_media_input(input_id=1),
        state=Onboarding.IMPORTANT_TODAY
    ),

    Window(
        Format("{difficult_today}"),
        BACK_NEXT_BTNS,
        create_text_input(input_id=2),
        create_media_input(input_id=2),
        state=Onboarding.DIFFICULT_TODAY
    ),

    Window(
        Format("{something_else}"),
        Row(
            Button(Format("{back_btn}"), id="back_btn_id", on_click=on_back),
            Button(Format("{next_btn}"), id="to_profile_btn_id", on_click=handle_profile),
        ),
        create_text_input(input_id=3),
        create_media_input(input_id=3),
        state=Onboarding.SOMETHING_ELSE
    ),

    Window(
        Format("{no_photo}"),
        Button(Format("{back_btn}"), id="back_btn_id", on_click=on_back),
        create_photo_input(input_id=4),
        state=Onboarding.NO_PHOTO
    ),

    Window(
        Format("{yes_photo}"),
        DynamicMedia('photo'),
        Row(
            Button(Format("{back_btn}"), id="back_btn_id", on_click=on_back),
            Button(Format("{yes_btn}"), id="yes_btn_id", on_click=confirm_photo_handler),
        ),
        create_photo_input(input_id=4),
        getter=photo_getter,
        state=Onboarding.PHOTO
    ),

    Window(
        Format("{step_1}"),
        BACK_NEXT_BTNS,
        create_text_input(input_id=5),
        create_media_input(input_id=5),
        state=Onboarding.STEP_1
    ),

    Window(
        Format("{background}"),
        BACK_NEXT_BTNS,
        create_text_input(input_id=6),
        create_media_input(input_id=6),
        state=Onboarding.BACKGROUND
    ),

    Window(
        Format("{step_2}"),
        BACK_NEXT_BTNS,
        create_text_input(input_id=7),
        create_media_input(input_id=7),
        state=Onboarding.STEP_2
    ),

    Window(
        Format("{step_3}"),
        BACK_NEXT_BTNS,
        create_text_input(input_id=8),
        create_media_input(input_id=8),
        state=Onboarding.STEP_3
    ),

    Window(
        Format("{step_4}"),
        BACK_NEXT_BTNS,
        create_text_input(input_id=9),
        create_media_input(input_id=9),
        state=Onboarding.STEP_4
    ),

    Window(
        Format("{step_5}"),
        BACK_NEXT_BTNS,
        create_text_input(input_id=10),
        create_media_input(input_id=10),
        state=Onboarding.STEP_5
    ),

    Window(
        Format("{step_6}"),
        BACK_NEXT_BTNS,
        create_text_input(input_id=11),
        create_media_input(input_id=11),
        state=Onboarding.STEP_6
    ),

    Window(
        Format("{thanks_btn}"),
        state=Onboarding.THANKS
    ),
    
    getter=dialog_get_data
)