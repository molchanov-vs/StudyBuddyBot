from typing import Any, TYPE_CHECKING

from aiogram.types import CallbackQuery
from aiogram.enums import ContentType

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Select, Back, Row, Button
from aiogram_dialog.widgets.text import Format, Jinja
from aiogram_dialog.widgets.media import StaticMedia

from ..widgets.scrolling_group import CustomScrollingGroup

from ..utils.utils import get_middleware_data

from ..states import StudentGallery
from ..custom_types import Student

from aiogram.enums import ParseMode
from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


async def on_dialog_start(
        start_data: Any,
        dialog_manager: DialogManager):

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


def prepare_list_of_students(dialog_manager: DialogManager) -> list[Student]:

    students_raw: list[dict] = dialog_manager.dialog_data["students"]
    students = [Student(**student) for student in students_raw]
    
    return students


async def get_students (
    dialog_manager: DialogManager, 
    **kwargs):


    _, _, user_data = get_middleware_data(dialog_manager)

    students: list[Student] = prepare_list_of_students(dialog_manager)

    students_list: list[tuple[str, int]] = [
        (f"{student.name} ⭐" if student.id == user_data.id else student.name, 
        int(student.id)) for student in students
    ]

    return {'students': students_list}


def get_indexes(dialog_manager: DialogManager) -> tuple[int, int, int]:

    return (
        dialog_manager.dialog_data.get("current_student_index"),
        dialog_manager.dialog_data.get("back_student_index"),
        dialog_manager.dialog_data.get("next_student_index")
    )


async def process_student_selection(
    callback: CallbackQuery, 
    widget: Select,
    dialog_manager: DialogManager, 
    item_id: str):

    current_student_id: int = int(item_id)
    students: list[Student] = prepare_list_of_students(dialog_manager)
    current_student_index: int = [s.id for s in students].index(current_student_id)

    dialog_manager.dialog_data["current_student_index"] = current_student_index

    dialog_manager.dialog_data["back_student_index"] = \
        current_student_index - 1 if current_student_index > 0 else len(students) - 1

    dialog_manager.dialog_data["next_student_index"] = \
        current_student_index + 1 if current_student_index < len(students) - 1 else 0

    await dialog_manager.next()


async def get_data_for_profile(
    dialog_manager: DialogManager,
    **kwargs):

    students: list[Student] = prepare_list_of_students(dialog_manager)
    data = {}

    current_student_index, back_student_index, next_student_index = get_indexes(dialog_manager)
    
    current_student: Student = students[current_student_index]
    
    # Apply character limit validation to current student before displaying
    current_student.validate_for_caption()  # Use caption limit (1024 chars) for media messages
    
    back_student: Student = students[back_student_index]
    next_student: Student = students[next_student_index]

    # Get validated formatted caption (guaranteed to be within limits)
    formatted_caption: str = current_student.get_validated_formatted_caption()
    
    # Add tags formatting (not included in Student class as it's optional)
    student_tags = f"\n#{' #'.join(current_student.tags)}" if current_student.tags else ""
    
    # Character limits are now handled at the Student level via get_validated_formatted_caption()

    data.update({
        "student_name": (current_student.name, current_student.username),
        "formatted_caption": f"<blockquote expandable>{formatted_caption}</blockquote>",  # Already formatted and validated
        "student_tags": student_tags,
        "back_student": f"{back_student.get_display_name()}",
        "next_student": f"{next_student.get_display_name()}"
    })

    if current_student.image_path:
        data.update({"student_image": 
        current_student.image_path
        })


    return data


def update_indexes(
    dialog_manager: DialogManager, 
    callback: CallbackQuery,
    num_students: int):

    current_student_index, _, _ = get_indexes(dialog_manager)
    
    match callback.data:
        case "back_student_id":
            current_student_index = current_student_index - 1 if current_student_index > 0 else num_students - 1
        case "next_student_id":
            current_student_index = current_student_index + 1 if current_student_index < num_students - 1 else 0

    dialog_manager.dialog_data["current_student_index"] = current_student_index
    dialog_manager.dialog_data["back_student_index"] = \
        current_student_index - 1 if current_student_index > 0 else num_students - 1
    dialog_manager.dialog_data["next_student_index"] = \
        current_student_index + 1 if current_student_index < num_students - 1 else 0


async def process_carousel(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    students: list[Student] = prepare_list_of_students(dialog_manager)

    update_indexes(dialog_manager, callback, len(students))


NAME_TEXT_WITH_USERNAME = Jinja("""
<a href="{{ student_name[1] }}"> {{ student_name[0] }}</a>
""")


dialog = Dialog(
    Window(
        Format("{students_header}"),

        CustomScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="student_list",
                item_id_getter=lambda item: item[1],
                items="students",
                on_click=process_student_selection
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


    Window(
        StaticMedia(
            path=Format("{student_image}"),
            type=ContentType.PHOTO, 
            when="student_image"),
        NAME_TEXT_WITH_USERNAME,
        Format("{formatted_caption}"),
        Format("{student_tags}"),
        Back(Format("{back_btn}")),
        Row(
            Button(Format("{back_student}"), id="back_student_id", on_click=process_carousel),
            Button(Format("{next_student}"), id="next_student_id", on_click=process_carousel),
        ),
        state=StudentGallery.PROFILE,
        getter=get_data_for_profile,
        parse_mode=ParseMode.HTML
    ),

    getter=dialog_get_data,
    on_start=on_dialog_start
)