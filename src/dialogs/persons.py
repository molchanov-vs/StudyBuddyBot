from typing import Any, TYPE_CHECKING

from aiogram import F

from aiogram.types import CallbackQuery
from aiogram.enums import ContentType

from aiogram_dialog import Dialog, Window, DialogManager, Data
from aiogram_dialog.widgets.kbd import Select, Back, Row, Button, Url
from aiogram_dialog.widgets.text import Format, Jinja, Const
from aiogram_dialog.widgets.media import StaticMedia

from ..widgets.scrolling_group import CustomScrollingGroup

from ..utils.utils import get_middleware_data

from ..states import PersonGallery, EditMode
from ..custom_types import Student, Teacher

from aiogram.enums import ParseMode
from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


async def on_dialog_start(
        start_data: Any,
        dialog_manager: DialogManager):

    dialog_manager.dialog_data["persons"] = start_data["persons"]
    dialog_manager.dialog_data["role"] = start_data["role"]
    dialog_manager.dialog_data["current_user_id"] = start_data.get("current_user_id", 0)
    dialog_manager.dialog_data["current_person_index"] = start_data.get("indexes", (0, 0, 0))[0]
    dialog_manager.dialog_data["back_person_index"] = start_data.get("indexes", (0, 0, 0))[1]
    dialog_manager.dialog_data["next_person_index"] = start_data.get("indexes", (0, 0, 0))[2]


async def dialog_get_data(
        i18n: TranslatorRunner,
        dialog_manager: DialogManager,
        **kwargs):

    data: dict[str, str] = {}
    data.update({
        "students_header": i18n.persons.students_header(),
        "teachers_header": i18n.persons.teachers_header(),
        "back_btn": i18n.service.back_btn(),
        "telegraph_btn": i18n.persons.telegraph_btn(),
        "edit_btn": i18n.edit.edit_btn(),
        "role": dialog_manager.dialog_data.get("role", "student"),
    })

    return data


def prepare_list_of_persons(dialog_manager: DialogManager) -> list[Student | Teacher]:

    persons_raw: list[dict] = dialog_manager.dialog_data.get("persons", [])

    if persons_raw[0]["role"] == "student":
        return [Student(**person) for person in persons_raw]
    else:
        return [Teacher(**person) for person in persons_raw]


async def get_persons(
    dialog_manager: DialogManager, 
    **kwargs):

    _, _, user_data = get_middleware_data(dialog_manager)

    persons: list[Student | Teacher] = prepare_list_of_persons(dialog_manager)

    persons_list: list[tuple[str, int]] = [
        (f"⭐ {person.name}" if person.id == user_data.id else person.name, 
        int(person.id)) for person in persons
    ]

    return {'persons': persons_list}


def get_indexes(dialog_manager: DialogManager) -> tuple[int, int, int]:

    return (
        dialog_manager.dialog_data.get("current_person_index"),
        dialog_manager.dialog_data.get("back_person_index"),
        dialog_manager.dialog_data.get("next_person_index")
    )


async def process_persons_selection(
    callback: CallbackQuery, 
    widget: Select,
    dialog_manager: DialogManager, 
    item_id: str):

    current_person_id: int = int(item_id)
    persons: list[Student | Teacher] = prepare_list_of_persons(dialog_manager)
    current_person_index: int = [p.id for p in persons].index(current_person_id)

    dialog_manager.dialog_data["current_person_index"] = current_person_index

    dialog_manager.dialog_data["back_person_index"] = \
        current_person_index - 1 if current_person_index > 0 else len(persons) - 1

    dialog_manager.dialog_data["next_person_index"] = \
        current_person_index + 1 if current_person_index < len(persons) - 1 else 0

    await dialog_manager.next()


async def get_data_for_profile(
    dialog_manager: DialogManager,
    **kwargs):

    _, config, user_data = get_middleware_data(dialog_manager)

    persons: list[Student | Teacher] = prepare_list_of_persons(dialog_manager)

    role = dialog_manager.dialog_data.get("role", "student")
    
    data = {}

    current_person_index, back_person_index, next_person_index = get_indexes(dialog_manager)
    
    current_person: Student | Teacher = persons[current_person_index]
    
    back_person: Student | Teacher = persons[back_person_index]
    next_person: Student | Teacher = persons[next_person_index]
    
    # Add tags formatting (not included in Student class as it's optional)
    person_tags = f"\n🏷️ #{' #'.join(current_person.tags)}" if current_person.tags else ""

    data.update({
        "person_name": (current_person.name, current_person.username),
        "person_slogan": f"\n💡 {current_person.slogan}" if current_person.slogan else "",
        "telegraph_page": current_person.telegraph_page,
        "person_tags": person_tags,
        "back_person": f"{back_person.get_display_name()}",
        "next_person": f"{next_person.get_display_name()}"
    })

    if role == "student":
        data.update({"person_expectations": f"\n🎯 {current_person.expectations}" if current_person.expectations else ""})
    else:
        data.update({"person_mission": f"\n🎯 {current_person.mission}" if current_person.mission else ""})

    if current_person.image_path:
        data.update({"person_image": 
        current_person.image_path
        })

    if current_person.id == dialog_manager.dialog_data.get("current_user_id", 0) or user_data.id in config.admins.ids:
        data.update({"edit_btn_true": True})

    
    dialog_manager.dialog_data["current_person_data"] = current_person.model_dump()

    return data


def update_indexes(
    dialog_manager: DialogManager, 
    callback: CallbackQuery,
    num_persons: int):

    current_person_index, _, _ = get_indexes(dialog_manager)
    
    match callback.data:
        case "back_person_id":
            current_person_index = current_person_index - 1 if current_person_index > 0 else num_persons - 1
        case "next_person_id":
            current_person_index = current_person_index + 1 if current_person_index < num_persons - 1 else 0

    dialog_manager.dialog_data["current_person_index"] = current_person_index
    dialog_manager.dialog_data["back_person_index"] = \
        current_person_index - 1 if current_person_index > 0 else num_persons - 1
    dialog_manager.dialog_data["next_person_index"] = \
        current_person_index + 1 if current_person_index < num_persons - 1 else 0


async def process_carousel(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    persons: list[Student | Teacher] = prepare_list_of_persons(dialog_manager)

    update_indexes(dialog_manager, callback, len(persons))


async def start_edit_mode(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    await dialog_manager.start(
        state=EditMode.MAIN,
        data={
            "current_person_data": dialog_manager.dialog_data.get("current_person_data", {}),
            "role": dialog_manager.dialog_data.get("role", "student"),
        }
    )
    

NAME_TEXT_WITH_USERNAME = Jinja("""
<a href="{{ person_name[1] }}"> 👤 {{ person_name[0] }}</a>
""")


async def on_process_result(
    start_data: Data,
    result: Any,
    dialog_manager: DialogManager):

    person: dict = result.get("person")
    persons: list[dict] = dialog_manager.dialog_data.get("persons")

    for p in persons:
        if p.get("id") == person.get("id"):
            p.update(person)
            break


dialog = Dialog(

    Window(
        Format("{students_header}", when=F["role"] == "student"),
        Format("{teachers_header}", when=F["role"] == "teacher"),

        CustomScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="person_list",
                item_id_getter=lambda item: item[1],
                items="persons",
                on_click=process_persons_selection
            ),
            width=1,
            height=5,
            id="person_croll_list_id",
            back_btn="◀️",
            forward_btn="▶️",
            back_btn_text="Назад"
        ),
        getter=get_persons,
        state=PersonGallery.SCROLL_LIST
    ),

    Window(
        StaticMedia(
            path=Format("{person_image}"),
            type=ContentType.PHOTO, 
            when="person_image"),
        NAME_TEXT_WITH_USERNAME,
        Format("{person_slogan}", when=F["person_slogan"]),
        Format("{person_expectations}", when=F["person_expectations"]),
        Format("{person_tags}", when=F["person_tags"]),
        Row(
            Url(text=Format("{telegraph_btn}"), url=Format("{telegraph_page}"), id="url_id"),
            Button(
                Format("{edit_btn}"), 
                id="edit_btn_id", 
                when="edit_btn_true", 
                on_click=start_edit_mode)
        ),
        
        Row(
            Button(Format("{back_person}"), id="back_person_id", on_click=process_carousel),
            Back(Const("Назад")),
            Button(Format("{next_person}"), id="next_person_id", on_click=process_carousel),
        ),
        state=PersonGallery.PROFILE,
        getter=get_data_for_profile,
        parse_mode=ParseMode.HTML
    ),

    getter=dialog_get_data,
    on_start=on_dialog_start,
    on_process_result=on_process_result
)