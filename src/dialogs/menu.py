from typing import TYPE_CHECKING

from glob import glob

from aiogram.types import CallbackQuery

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog import StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from ..states import Flow, PersonGallery
from ..custom_types import Student, Teacher
from ..google_queries import get_students, get_teachers

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

    state = PersonGallery.SCROLL_LIST

    match callback.data:

        case "student_gallery_btn_id":
            role = "student"
            persons: list[Student] = await get_students(config)

        case "teacher_gallery_btn_id":
            role = "teacher"
            persons: list[Teacher] = await get_teachers(config)
            
        case "my_profile_btn_id":
            # For my profile, we need to determine if user is student or teacher
            # and get the appropriate list
            students: list[Student] = await get_students(config)
            teachers: list[Teacher] = await get_teachers(config)
            
            # Check if user is in students or teachers list
            if any(s.id == user_data.id for s in students):
                role = "student"
                persons = students
            elif any(t.id == user_data.id for t in teachers):
                role = "teacher"
                persons = teachers
            else:
                # User not found in either list, default to students
                role = "unknown"
                persons = students

    if role == "unknown":
        await bot.send_message(chat_id=user_data.id, text="Похоже ты не студент или не преподаватель. Пожалуйста, обратитесь к <a href='https://t.me/anastasia_ilu'>Насте</a>")
        await dialog_manager.start(
            state=Flow.MENU, 
            mode = StartMode.RESET_STACK,
            show_mode=ShowMode.DELETE_AND_SEND)
        return

    if user_data.id not in config.admins.ids:
        persons = [p for p in persons if p.id not in config.admins.ids]

    all_images: list[str] = glob("./media/*/onboarding/4_*")

    for person in persons:
        person.get_latest_image_path(all_images)
        
    start_data = {
        "role": role,
        "persons": [p.model_dump() for p in persons],
        "current_user_id": user_data.id
    }

    if callback.data == "my_profile_btn_id":
        state = PersonGallery.PROFILE
        current_student_index: int = [p.id for p in persons].index(user_data.id)
        back_student_index: int = current_student_index - 1 if current_student_index > 0 else len(persons) - 1
        next_student_index: int = current_student_index + 1 if current_student_index < len(persons) - 1 else 0
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