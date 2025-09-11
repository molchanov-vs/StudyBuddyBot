from typing import TYPE_CHECKING

from glob import glob

from aiogram.types import CallbackQuery

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from ..states import Flow, StudentGallery
from ..custom_types import Student
from ..google_queries import get_students

from ..utils.utils import get_middleware_data

from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


async def dialog_get_data(
        i18n: TranslatorRunner,
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
async def retrive_gallery(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    bot, config, user_data = get_middleware_data(dialog_manager)
    students: list[Student] = await get_students(config)

    if user_data.id not in config.admins.ids:
        students = [s for s in students if s.id not in config.admins.ids]

    all_images: list[str] = glob("./media/*/onboarding/4_*")

    for student in students:
        student.get_latest_image_path(all_images)

    start_data = {
        "students": [s.model_dump() for s in students],
        "current_user_id": user_data.id
    }

    match callback.data:

        case "student_gallery_btn_id":
            state = StudentGallery.SCROLL_LIST

        case "my_profile_btn_id":
            state = StudentGallery.PROFILE
            current_student_index: int = [s.id for s in students].index(user_data.id)
            back_student_index: int = current_student_index - 1 if current_student_index > 0 else len(students) - 1
            next_student_index: int = current_student_index + 1 if current_student_index < len(students) - 1 else 0
            start_data.update({
                "indexes": (current_student_index, back_student_index, next_student_index)
            })

    await dialog_manager.start(
        state=state,
        data=start_data
        )
        

dialog = Dialog(
    Window(
        Format("{menu_header}"),

        Button(
            Format("{student_gallery_btn}"), 
            id="student_gallery_btn_id", 
            on_click=retrive_gallery
            ),

        Button(
            Format("{teacher_gallery_btn}"), 
            id="teacher_gallery_btn_id",
            on_click=retrive_gallery
            ),
        Button(Format("{schedule_btn}"), id="schedule_btn_id", when="schedule"),
        Button(
            Format("{my_profile_btn}"), 
            id="my_profile_btn_id", 
            on_click=retrive_gallery
            ),
        state=Flow.MENU,
    ),

    getter=dialog_get_data
)