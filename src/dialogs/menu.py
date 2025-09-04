from typing import TYPE_CHECKING

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Row, Next, Back
from aiogram_dialog.widgets.text import Format

from ..states import Flow

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



dialog = Dialog(
    Window(
        Format("{menu_header}"),
        Button(Format("{student_gallery_btn}"), id="student_gallery_btn_id"),
        Button(Format("{teacher_gallery_btn}"), id="teacher_gallery_btn_id"),
        Button(Format("{schedule_btn}"), id="schedule_btn_id", when="schedule"),
        Button(Format("{my_profile_btn}"), id="my_profile_btn_id"),
        state=Flow.MENU,
    ),

    getter=dialog_get_data
)