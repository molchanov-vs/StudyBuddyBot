from typing import Any, TYPE_CHECKING

from aiogram.types import CallbackQuery
from aiogram.enums import ContentType

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Row, Next, Back
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput

from ..utils.boarding_handlers import correct_name_handler, error_name_handler
from ..utils.utils import get_middleware_data

from ..google_queries import update_cell_by_coordinates

from ..states import EditMode

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


async def start_edit_photo(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=EditMode.EDIT_PHOTO,
        data={"current_student_data": dialog_manager.dialog_data.get("current_student_data", 0)}
    )

async def start_edit_name(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    await dialog_manager.switch_to(EditMode.EDIT_NAME)


async def getter_edit_name(dialog_manager: DialogManager, **kwargs):

    student: Student = Student(**dialog_manager.dialog_data.get("student"))
    data: dict[str, str] = {"name": f"<b>{student.name}</b>"}
    print(student.model_dump_json(indent=4))

    if dialog_manager.dialog_data.get("edit_mode"):
        data.update({"edit_mode": True})

    return data


async def start_edit_slogan(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=EditMode.EDIT_SLOGAN,
        data={"current_student_data": dialog_manager.dialog_data.get("current_student_data", 0)}
    )

async def start_edit_prof_experience(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=EditMode.EDIT_PROF_EXPERIENCE,
        data={"current_student_data": dialog_manager.dialog_data.get("current_student_data", 0)}
    )

async def start_edit_about(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=EditMode.EDIT_ABOUT,
        data={"current_student_data": dialog_manager.dialog_data.get("current_student_data", 0)}
    )

async def start_edit_tags(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=EditMode.EDIT_TAGS,
        data={"current_student_data": dialog_manager.dialog_data.get("current_student_data", 0)}
    )

async def start_edit_expectations(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=EditMode.EDIT_EXPECTATIONS,
        data={"current_student_data": dialog_manager.dialog_data.get("current_student_data", 0)}
    )


async def process_done(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    _,config, user_data = get_middleware_data(dialog_manager)

    current_state = dialog_manager.current_context().state
    print("current_state", current_state)

    match current_state:
        case EditMode.EDIT_NAME:

            column = 1
            row = dialog_manager.dialog_data.get("student").get("row")
            value = dialog_manager.dialog_data.get("student").get("name")
            print("coords", column, row)

        case _:
            pass

            
    await update_cell_by_coordinates(
        config=config,
        sheet_name=config.google.vitrina_tab,
        column=column + 1,
        row=row,
        value=value
    )


    await dialog_manager.done(result={"student": dialog_manager.dialog_data.get("student")})


dialog = Dialog(
    Window(
        Format("{edit_header}"),
        Button(Format("{edit_photo_btn}"), id="edit_photo_btn_id", on_click=start_edit_photo),
        Button(Format("{edit_name_btn}"), id="edit_name_btn_id", on_click=start_edit_name),
        Button(Format("{edit_slogan_btn}"), id="edit_slogan_btn_id", on_click=start_edit_slogan),
        Button(Format("{edit_prof_experience_btn}"), id="edit_prof_experience_btn_id", on_click=start_edit_prof_experience),
        Button(Format("{edit_about_btn}"), id="edit_about_btn_id", on_click=start_edit_about),
        Button(Format("{edit_tags_btn}"), id="edit_tags_btn_id", on_click=start_edit_tags),
        Button(Format("{edit_expectations_btn}"), id="edit_expectations_btn_id", on_click=start_edit_expectations),
        Back(Format("{back_btn}")),
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

        Row(
            Back(Format("{back_btn}")),
            Button(Format("{done_btn}"), id="done_btn_id", on_click=process_done, when="edit_mode"),
        ),

        getter=getter_edit_name,
        state=EditMode.EDIT_NAME,
    ),

    getter=dialog_get_data,
    on_start=on_dialog_start
)