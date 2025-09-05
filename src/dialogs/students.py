from typing import Any, TYPE_CHECKING

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Select
from aiogram_dialog.widgets.text import Format

from ..widgets.scrolling_group import CustomScrollingGroup

from ..utils.utils import get_middleware_data

from ..states import StudentGallery
from ..custom_types import Student

from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


async def on_dialog_start(
        start_data: Any,
        dialog_manager: DialogManager):

    # data: dict[str, Any] = start_data

    dialog_manager.dialog_data["students"] = start_data["students"]


async def dialog_get_data(
        i18n: TranslatorRunner,
        dialog_manager: DialogManager,
        **kwargs):

    data: dict[str, str] = {}
    data.update({
        "students_header": i18n.students.students_header(),
        "back_btn": i18n.service.back_btn(),
    })

    return data


async def get_students (
    dialog_manager: DialogManager, 
    **kwargs):

    _, _, user_data = get_middleware_data(dialog_manager)

    students_raw: list[dict] = dialog_manager.dialog_data["students"]
    students: list[Student] = [Student(**student) for student in students_raw]

    students = [
        (f"{student.name} ⭐" if student.id == user_data.id else student.name, 
        int(student.id)) for student in students
    ]

    return {'students': students}


dialog = Dialog(
    Window(
        Format("{students_header}"),

        CustomScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="student_list",
                item_id_getter=lambda item: item[1],
                items="students",
            ),
            width=1,
            height=5,
            id="student_croll_list_id",
            back_btn="◀️",
            forward_btn="▶️",
            back_btn_text="Назад"
        ),
        getter=get_students,
        state=StudentGallery.SCROLL_LIST
    ),

    getter=dialog_get_data,
    on_start=on_dialog_start
)