from typing import TYPE_CHECKING

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Row, Next, Back
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.media import DynamicMedia

from ..utils.boarding_handlers import on_approve,\
    name_check, correct_name_handler, error_name_handler, \
        handle_profile, confirm_photo_handler, \
            photo_getter, create_text_input, create_media_input, create_photo_input, \
                go_back, go_next

from ..utils.utils import load_locales

from ..states import Onboarding

from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


async def dialog_get_data(
        i18n: TranslatorRunner,
        dialog_manager: DialogManager,
        **kwargs):
    
    data: dict[str, str] = load_locales(i18n, dialog_manager)

    # for back_btn
    current_state = dialog_manager.current_context().state
    if current_state not in [Onboarding.WELCOME, Onboarding.PREONBOARDING, Onboarding.NAME]:
        data.update({"can_go_back": True})

    if "visited" not in dialog_manager.dialog_data:
        dialog_manager.dialog_data["visited"] = []
    else:
        if current_state.state not in dialog_manager.dialog_data["visited"]:
            dialog_manager.dialog_data["visited"].append(current_state.state)

    list_of_states = list(Onboarding.__state_names__)
    current_index = list_of_states.index(current_state.state)
    next_state = list_of_states[current_index + 1] if current_index < len(list_of_states) - 1 else None
    if next_state in dialog_manager.dialog_data["visited"]:
        data.update({"can_go_next": True})

    return data


BACK_NEXT_BTNS = Row(
    Button(Format("{back_btn}"), id="back_btn_id", on_click=go_back, when="can_go_back"),
    Button(Format("{next_btn}"), id="next_btn_id", on_click=go_next, when="can_go_next")
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
        BACK_NEXT_BTNS,
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
            Back(Format("{back_btn}")),
            Button(Format("{next_btn}"), id="to_profile_btn_id", on_click=handle_profile),
        ),
        create_text_input(input_id=3),
        create_media_input(input_id=3),
        state=Onboarding.SOMETHING_ELSE
    ),

    Window(
        Format("{no_photo}"),
        Button(Format("{back_btn}"), id="back_btn_id", on_click=go_back),
        create_photo_input(input_id=4),
        state=Onboarding.NO_PHOTO
    ),

    Window(
        Format("{yes_photo}"),
        DynamicMedia('photo'),
        Row(
            Button(Format("{back_btn}"), id="back_btn_id", on_click=go_back),
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
    
    getter=dialog_get_data,
)