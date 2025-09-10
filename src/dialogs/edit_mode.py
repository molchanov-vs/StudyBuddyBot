from typing import Any, TYPE_CHECKING

import re

from aiogram.types import CallbackQuery, Message
from aiogram.enums import ContentType

from aiogram_dialog import Dialog, Window, DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.kbd import Button, Row, Start, Back
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput, ManagedTextInput

from ..utils.boarding_handlers import correct_name_handler, error_name_handler
from ..utils.utils import get_middleware_data

from ..google_queries import update_cell_by_coordinates

from ..states import EditMode, Flow

from ..enums import ButtonsId

from ..custom_types import Student

from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


async def on_dialog_start(
        start_data: Any,
        dialog_manager: DialogManager):

    dialog_manager.dialog_data["student"] = start_data["current_student_data"]


async def dialog_get_data(
        i18n: TranslatorRunner,
        dialog_manager: DialogManager,
        **kwargs):

    data: dict[str, str] = {}
    data.update({
        "edit_header": i18n.edit.edit_header(),
        "edit_photo_btn": i18n.edit.edit_photo_btn(),
        "edit_name_btn": i18n.edit.edit_name_btn(),
        "edit_slogan_btn": i18n.edit.edit_slogan_btn(),
        "edit_prof_experience_btn": i18n.edit.edit_prof_experience_btn(),
        "edit_about_btn": i18n.edit.edit_about_btn(),
        "edit_tags_btn": i18n.edit.edit_tags_btn(),
        "edit_expectations_btn": i18n.edit.edit_expectations_btn(),
        "done_btn": i18n.service.done_btn(),
        "back_btn": i18n.service.back_btn(),
    })

    return data


async def start_edit_photo(
    callback: CallbackQuery, 
    button: Button, 
    dialog_manager: DialogManager):

    pass
    # await dialog_manager.start(
    #     state=EditMode.EDIT_PHOTO,
    #     data={"current_student_data": dialog_manager.dialog_data.get("current_student_data", 0)}
    # )

async def start_edit_mode(
    callback: CallbackQuery, 
    button: Button, 
    dialog_manager: DialogManager):

    match callback.data:

        case ButtonsId.EDIT_SLOGAN_BTN_ID:
            mode = EditMode.EDIT_SLOGAN

        case ButtonsId.EDIT_PROF_EXPERIENCE_BTN_ID:
            mode = EditMode.EDIT_PROF_EXPERIENCE

        case ButtonsId.EDIT_ABOUT_BTN_ID:
            mode = EditMode.EDIT_ABOUT

        case ButtonsId.EDIT_TAGS_BTN_ID:
            mode = EditMode.EDIT_TAGS

        case ButtonsId.EDIT_EXPECTATIONS_BTN_ID:
            mode = EditMode.EDIT_EXPECTATIONS

        case ButtonsId.EDIT_NAME_BTN_ID:
            mode = EditMode.EDIT_NAME

        case ButtonsId.EDIT_PHOTO_BTN_ID:
            mode = EditMode.EDIT_PHOTO

        case _:
            pass

    await dialog_manager.switch_to(mode)


async def getter_for_edition(dialog_manager: DialogManager, **kwargs):

    student: Student = Student(**dialog_manager.dialog_data.get("student"))

    data: dict[str, str] = {
        "name": f"<b>{student.name}</b>",
        "slogan": f"<b>{student.slogan}</b>",
        "prof_experience": f"<b>{student.prof_experience}</b>",
        "about": f"<b>{student.about}</b>",
        "tags": f"<b>{student.tags}</b>",
        "expectations": f"<b>{student.expectations}</b>"
    }

    if dialog_manager.dialog_data.get("edit_mode"):
        data.update({"edit_mode": True})

    return data


async def process_done(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    _,config, _ = get_middleware_data(dialog_manager)

    current_state = dialog_manager.current_context().state

    row = dialog_manager.dialog_data.get("student").get("row")

    match current_state:

        case EditMode.EDIT_NAME:
            column = 1
            value = "name"

        case EditMode.EDIT_SLOGAN:

            column = 7
            value = "slogan"

        case EditMode.EDIT_PROF_EXPERIENCE:
            column = 8
            value = "prof_experience"

        case EditMode.EDIT_ABOUT:
            column = 9
            value = "about"

        case EditMode.EDIT_TAGS:
            column = 11
            value = "tags"

        case EditMode.EDIT_EXPECTATIONS:
            column = 14
            value = "expectations"

        case _:
            pass

            
    await update_cell_by_coordinates(
        config=config,
        sheet_name=config.google.vitrina_tab,
        column=column + 1,
        row=row,
        value=dialog_manager.dialog_data.get("student").get(value)
    )

    await dialog_manager.done(result={"student": dialog_manager.dialog_data.get("student")})


async def correct_input_handler(
        message: Message, 
        widget: ManagedTextInput, 
        dialog_manager: DialogManager, 
        text: str) -> None:

    current_state = dialog_manager.current_context().state

    match current_state:

        case EditMode.EDIT_SLOGAN:
            value = "slogan"

        case EditMode.EDIT_PROF_EXPERIENCE:
            value = "prof_experience"

        case EditMode.EDIT_ABOUT:
            value = "about"

        case EditMode.EDIT_TAGS:
            value = "tags"
            tokens = re.split(r"[,\s]+", text.strip())
            text = "\n".join([t.lstrip('#') for t in tokens if t])

        case EditMode.EDIT_EXPECTATIONS:
            value = "expectations"

        case _:
            pass

    dialog_manager.dialog_data["student"][value] = text
    dialog_manager.dialog_data["edit_mode"] = True


BACK_DONE_BTNS = Row(
    Back(Format("{back_btn}")),
    Button(Format("{done_btn}"), id="done_btn_id", on_click=process_done, when="edit_mode")
    )


dialog = Dialog(
    Window(
        Format("{edit_header}"),

        Button(
            Format("{edit_photo_btn}"), 
            id=ButtonsId.EDIT_PHOTO_BTN_ID, 
            on_click=start_edit_mode),

        Button(
            Format("{edit_name_btn}"), 
            id=ButtonsId.EDIT_NAME_BTN_ID, 
            on_click=start_edit_mode),

        Button(
            Format("{edit_slogan_btn}"), 
            id=ButtonsId.EDIT_SLOGAN_BTN_ID, 
            on_click=start_edit_mode),

        Button(
            Format("{edit_prof_experience_btn}"), 
            id=ButtonsId.EDIT_PROF_EXPERIENCE_BTN_ID, 
            on_click=start_edit_mode),

        Button(
            Format("{edit_about_btn}"), 
            id=ButtonsId.EDIT_ABOUT_BTN_ID, 
            on_click=start_edit_mode),

        Button(
            Format("{edit_tags_btn}"), 
            id=ButtonsId.EDIT_TAGS_BTN_ID, 
            on_click=start_edit_mode),

        Button(
            Format("{edit_expectations_btn}"), 
            id=ButtonsId.EDIT_EXPECTATIONS_BTN_ID, 
            on_click=start_edit_mode),

        Start(
            Format("{back_btn}"),
            id="back_btn",
            state=Flow.MENU,
            show_mode=ShowMode.DELETE_AND_SEND,
            mode=StartMode.RESET_STACK
        ),
        state=EditMode.MAIN,
    ),

    Window(
        Const("Текущее имя:"),
        Format("{name}"),
        TextInput(
            id="name_input",
            on_success=correct_name_handler,
            on_error=error_name_handler,
        ),
        BACK_DONE_BTNS,
        getter=getter_for_edition,
        state=EditMode.EDIT_NAME,
    ),

    Window(
        Const("Текущий слоган:"),
        Format("{slogan}"),
        TextInput(
            id="slogan_input",
            on_success=correct_input_handler
        ),
        BACK_DONE_BTNS,
        getter=getter_for_edition,
        state=EditMode.EDIT_SLOGAN,
    ),

    Window(
        Const("Текущий профессиональный опыт:"),
        Format("{prof_experience}"),
        TextInput(
            id="prof_experience_input",
            on_success=correct_input_handler
        ),
        BACK_DONE_BTNS,
        getter=getter_for_edition,
        state=EditMode.EDIT_PROF_EXPERIENCE,
    ),

    Window(
        Const("Текущий о себе:"),
        Format("{about}"),
        TextInput(
            id="about_input",
            on_success=correct_input_handler
        ),
        BACK_DONE_BTNS,
        getter=getter_for_edition,
        state=EditMode.EDIT_ABOUT,
    ),

    Window(
        Const("Текущие теги:"),
        Format("{tags}"),
        TextInput(
            id="tags_input",
            on_success=correct_input_handler
        ),
        BACK_DONE_BTNS,
        getter=getter_for_edition,
        state=EditMode.EDIT_TAGS,
    ),


    Window(
        Const("Текущие ожидания:"),
        Format("{expectations}"),
        TextInput(
            id="expectations_input",
            on_success=correct_input_handler
        ),
        BACK_DONE_BTNS,
        getter=getter_for_edition,
        state=EditMode.EDIT_EXPECTATIONS,
    ),

    getter=dialog_get_data,
    on_start=on_dialog_start
)