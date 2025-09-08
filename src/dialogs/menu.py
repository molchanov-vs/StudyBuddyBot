from typing import TYPE_CHECKING

from glob import glob

from aiogram.types import CallbackQuery

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Start
from aiogram_dialog.widgets.text import Format

from ..states import Flow, StudentGallery
from ..custom_types import Student
from ..google_queries import get_students, get_start_data_for_dialog

from ..utils.utils import get_middleware_data

from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


async def dialog_get_data(
        i18n: TranslatorRunner,
        dialog_manager: DialogManager,
        **kwargs):

        data: dict[str, str] = {}
        data.update({
            "menu_btn": i18n.menu.menu_btn(),
            "menu_header": i18n.menu.menu_header(),
            "student_gallery_btn": i18n.menu.student_gallery_btn(),
            "teacher_gallery_btn": i18n.menu.teacher_gallery_btn(),
            "schedule_btn": i18n.menu.schedule_btn(),
            "my_profile_btn": i18n.menu.my_profile_btn(),
        })

        return data



# Callback handlers for the buttons
async def start_student_gallery(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    _,config, _ = get_middleware_data(dialog_manager)
    students: list[Student] = await get_students(config)

    all_images: list[str] = glob("./media/*/onboarding/4_*")

    for student in students:
        student.get_latest_image_path(all_images)

    await dialog_manager.start(
        state=StudentGallery.SCROLL_LIST,
        data={
            "students": [s.model_dump() for s in students]
            }
        )


dialog = Dialog(
    Window(
        Format("{menu_header}"),

        Button(
            Format("{student_gallery_btn}"), 
            id="student_gallery_btn_id", 
            on_click=start_student_gallery
            ),

        Button(Format("{teacher_gallery_btn}"), id="teacher_gallery_btn_id"),
        Button(Format("{schedule_btn}"), id="schedule_btn_id", when="schedule"),
        Button(Format("{my_profile_btn}"), id="my_profile_btn_id"),
        state=Flow.MENU,
    ),

    getter=dialog_get_data
)