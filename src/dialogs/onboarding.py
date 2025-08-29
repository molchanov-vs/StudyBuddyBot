from typing import TYPE_CHECKING

import asyncio


from aiogram.types import Message
from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Next, Back
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram.fsm.storage.redis import RedisStorage

from my_tools import get_datetime_now, DateTimeKeys

from ..utils.boarding_handlers import on_approve, \
    name_check, correct_name_handler, error_name_handler, text_input_handler

from ..utils.utils import get_middleware_data, load_locales

from ..states import Onboarding
from ..config import Config

from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


async def dialog_get_data(
        i18n: TranslatorRunner,
        users: RedisStorage,
        dialog_manager: DialogManager,
        **kwargs):
    
    _, _, user_data = get_middleware_data(dialog_manager)
    
    data: dict[str, str] = load_locales(i18n, dialog_manager)

    return data


# Хэндлер, который сработает, если пользователь отправил вообще не текст
async def handle_voice_and_video_note(message: Message, widget: MessageInput, dialog_manager: DialogManager):

    bot, _, user_data = get_middleware_data(dialog_manager)

    # print(message.model_dump_json(indent=4, exclude_none=True))

    date: str = get_datetime_now(DateTimeKeys.DEFAULT)

    if message.voice:
        await bot.download(
            file=message.voice.file_id, 
            destination=f"media/{user_data.id}/onboarding/{date}.ogg"
            )

    if message.video_note:
        await bot.download(
            file=message.video_note.file_id, 
            destination=f"media/{user_data.id}/onboarding/{date}.mp4"
            )

    await message.answer(text='Вы добавили не текст')
    await dialog_manager.next()


async def handle_other(message: Message, widget: MessageInput, dialog_manager: DialogManager):

    await message.answer(text='❗Это должен быть текст, голосовое или кружочек')
    await asyncio.sleep(1)


MESSAGE_INPUT = MessageInput(
        func=handle_voice_and_video_note,
        content_types= [ContentType.VOICE, ContentType.VIDEO_NOTE]
    )


INCORRECT_INPUT = MessageInput(
        func=handle_other,
        content_types= ContentType.ANY
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
        Back(Format("{back_btn}"), id="back_btn_id"),
        TextInput(
            id='important_today_text_input',
            on_success=text_input_handler
        ),
        MESSAGE_INPUT,
        INCORRECT_INPUT,
        state=Onboarding.IMPORTANT_TODAY
    ),

    Window(
        Format("{difficult_today}"),
        TextInput(
            id='difficult_today_text_input',
            on_success=text_input_handler
        ),
        MESSAGE_INPUT,
        INCORRECT_INPUT,
        state=Onboarding.DIFFICULT_TODAY
    ),

    Window(
        Format("{something_else}"),
        Next(Format("{to_profile_btn}"), id="to_profile_btn_id"),
        TextInput(
            id='something_else_text_input',
            on_success=text_input_handler
        ),
        MESSAGE_INPUT,
        INCORRECT_INPUT,
        state=Onboarding.SOMETHING_ELSE
    ),

#     Window(
#         Format("{current_status}"),
#         Button(Format("{offline_status_btn}"), id="offline", on_click=handle_status),
#         Button(Format("{online_status_btn}"), id="online", on_click=handle_status),
#         Button(Format("{staff_status_btn}"), id="staff", on_click=handle_status),
#         state=Onboarding.CURRENT_STATUS
#     ),

#    Window(
#         Format("{university}"),
#         Button(Format("{mipt_btn}"), id="mipt", on_click=handle_university),
#         Button(Format("{other_btn}"), id="other", on_click=handle_university),
#         state=Onboarding.UNIVERSITY
#     ),

#     Window(
#         Format("{about_bot}"),
#         Row(
#             Button(Format("{newsletter_btn}"), id="newsletter", on_click=handle_about),
#             Button(Format("{friends_btn}"), id="friends", on_click=handle_about),
#         ),
#         Button(Format("{socials_btn}"), id="socials", on_click=handle_about),
#         state=Onboarding.ABOUT
#     ),

#     Window(
#         Format("{clarify_message}"),
#         TextInput(
#             id='clarify_input',
#             on_success=handle_clarify,
#         ),
#         state=Onboarding.CLARIFY
#     ),

#     Window(
#         Format("{person_welcome_msg}"),
#         Button(Format("{lets_start}"), id="start_interaction", on_click=start_interaction),
#         state=Onboarding.PERSON
#     ),

#     Window(
#         Format("{question_1}"),
#         NUMS,
#         state=Onboarding.QUESTION_1,
#         getter=get_numbers
#     ),

#     Window(
#         Format("{question_2}"),
#         NUMS,
#         state=Onboarding.QUESTION_2,
#         getter=get_numbers
#     ),

#     Window(
#         Format("{question_3}"),
#         NUMS,
#         state=Onboarding.QUESTION_3,
#         getter=get_numbers
#     ),

#     Window(
#         Format("{question_4}"),
#         NUMS,
#         state=Onboarding.QUESTION_4,
#         getter=get_numbers
#     ),

#     Window(
#         Format("{thanks_msg}"),
#         TextInput(
#             id='chat_input',
#             on_success=chat_handler,
#         ),
#         state=Onboarding.CHAT
#     ),

    getter=dialog_get_data
)