from typing import TYPE_CHECKING

import random

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Next
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram.fsm.storage.redis import RedisStorage

from ..utils.boarding_handlers import on_approve

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
    
    data = load_locales(i18n)

    return data


# Dialog with windows using Format for localization
dialog = Dialog(

    Window(
        Format("{welcome}"),
        Next(Format("{super_btn}"), id="super_btn_id"),
        state=Onboarding.WELCOME
    ),

    Window(
        Format("{welcome}"),
        Button(Format("{approve_btn}"), id="approve", on_click=on_approve),
        state=Onboarding.PREONBOARDING
    ),

    # Window(
    #     Format("{name}"),
    #     TextInput(
    #         id='name_input',
    #         on_success=correct_name_handler,
    #     ),
    #     state=Onboarding.NAME
    # ),

    # Window(
    #     Format("{important_today}"),
    #     TextInput(
    #         id='important_today_text_input',
    #         type_factory=age_check,
    #         on_success=correct_age_handler,
    #         on_error=error_age_handler,
    #     ),
    #     MessageInput(),
    #     state=Onboarding.IMPORTANT_TODAY
    # ),

#     Window(
#         Format("{important_today}"),
#         TextInput(
#             id='age_input',
#             type_factory=age_check,
#             on_success=correct_age_handler,
#             on_error=error_age_handler,
#         ),
#         MessageInput(),
#         state=Onboarding.DIFFICULT_TODAY
#     ),

#     Window(
#         Format("{education}"),
#         Button(Format("{bachelor_btn}"), id="bachelor", on_click=handle_education),
#         Button(Format("{master_btn}"), id="master", on_click=handle_education),
#         state=Onboarding.EDUCATION
#     ),

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