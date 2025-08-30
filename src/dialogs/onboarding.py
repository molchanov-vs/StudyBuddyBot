from typing import TYPE_CHECKING

import asyncio


from aiogram.types import Message
from aiogram.enums import ContentType
from aiogram.fsm.storage.redis import RedisStorage

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Next, Back, Row
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.media import DynamicMedia


from my_tools import get_datetime_now, DateTimeKeys

from ..utils.boarding_handlers import on_approve, \
    name_check, correct_name_handler, error_name_handler, text_input_handler, \
        handle_profile

from ..utils.utils import get_middleware_data, load_locales

from ..utils.face_handlers import handle_photo

from ..states import Onboarding
from ..config import Config

from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


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

    return data


# Хэндлер, который сработает, если пользователь отправил вообще не текст
async def handle_voice_and_video_note(message: Message, widget: MessageInput, dialog_manager: DialogManager):

    bot, _, user_data = get_middleware_data(dialog_manager)

    # print(message.model_dump_json(indent=4, exclude_none=True))

    date: str = get_datetime_now(DateTimeKeys.DEFAULT)

    if message.voice or message.video_note:
        if message.voice:
            await bot.download(
                file=message.voice.file_id, 
                destination=f"media/{user_data.id}/onboarding/{date}.ogg"
                )
            await dialog_manager.next()

        if message.video_note:
            await bot.download(
                file=message.video_note.file_id, 
                destination=f"media/{user_data.id}/onboarding/{date}.mp4"
                )
            await dialog_manager.next()
    else:
        await message.answer(text='❗Это должен быть текст, голосовое или кружочек')
        await asyncio.sleep(1)


MEDIA_INPUT = MessageInput(
        func=handle_voice_and_video_note,
        content_types= [ContentType.VOICE, ContentType.VIDEO_NOTE]
    )


PHOTO_INPUT = MessageInput(
        func=handle_photo,
        content_types= ContentType.PHOTO
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
        MEDIA_INPUT,
        state=Onboarding.IMPORTANT_TODAY
    ),

    Window(
        Format("{difficult_today}"),
        Back(Format("{back_btn}"), id="back_btn_id"),
        TextInput(
            id='difficult_today_text_input',
            on_success=text_input_handler
        ),
        MEDIA_INPUT,
        state=Onboarding.DIFFICULT_TODAY
    ),

    Window(
        Format("{something_else}"),
        Row(
            Back(Format("{back_btn}"), id="back_btn_id"),
            Button(Format("{next_btn}"), id="to_profile_btn_id", on_click=handle_profile),
        ),
        TextInput(
            id='something_else_text_input',
            on_success=text_input_handler
        ),
        MEDIA_INPUT,
        state=Onboarding.SOMETHING_ELSE
    ),

    Window(
        Format("{no_photo}"),
        Back(Format("{back_btn}"), id="back_btn_id"),
        PHOTO_INPUT,
        state=Onboarding.NO_PHOTO
    ),

    Window(
        Format("{yes_photo}"),
        DynamicMedia('photo'),
        Back(Format("{back_btn}"), id="back_btn_id"),
        Button(Format("{yes_btn}"), id="yes_btn_id", on_click=handle_photo),
        PHOTO_INPUT,
        getter=photo_getter,
        state=Onboarding.PHOTO
    ),

    Window(
        Format("{step_1}"),
        Back(Format("{back_btn}"), id="back_btn_id"),
        TextInput(
            id='step_1_text_input',
            on_success=text_input_handler
        ),
        MEDIA_INPUT,
        state=Onboarding.STEP_1
    ),

    Window(
        Format("{background}"),
        Back(Format("{back_btn}"), id="back_btn_id"),
        TextInput(
            id='background_text_input',
            on_success=text_input_handler
        ),
        MEDIA_INPUT,
        state=Onboarding.BACKGROUND
    ),

    Window(
        Format("{step_2}"),
        Back(Format("{back_btn}"), id="back_btn_id"),
        TextInput(
            id='step_2_text_input',
            on_success=text_input_handler
        ),
        MEDIA_INPUT,
        state=Onboarding.STEP_2
    ),

    Window(
        Format("{step_3}"),
        Back(Format("{back_btn}"), id="back_btn_id"),
        TextInput(
            id='step_3_text_input',
            on_success=text_input_handler
        ),
        MEDIA_INPUT,
        state=Onboarding.STEP_3
    ),

    Window(
        Format("{step_4}"),
        Back(Format("{back_btn}"), id="back_btn_id"),
        TextInput(
            id='step_4_text_input',
            on_success=text_input_handler
        ),
        MEDIA_INPUT,
        state=Onboarding.STEP_4
    ),

    Window(
        Format("{step_5}"),
        Back(Format("{back_btn}"), id="back_btn_id"),
        TextInput(
            id='step_5_text_input',
            on_success=text_input_handler
        ),
        MEDIA_INPUT,
        state=Onboarding.STEP_5
    ),

    Window(
        Format("{step_6}"),
        Back(Format("{back_btn}"), id="back_btn_id"),
        TextInput(
            id='step_6_text_input',
            on_success=text_input_handler
        ),
        MEDIA_INPUT,
        state=Onboarding.STEP_6
    ),

    Window(
        Format("{thanks_btn}"),
        state=Onboarding.THANKS
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