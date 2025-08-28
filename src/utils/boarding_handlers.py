from typing import Any, TYPE_CHECKING

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.state import State

from ..enums import Database, Action
from ..states import Onboarding
from ..custom_types import UserOnboarding, UserOffboarding
from .utils import get_current_state
from ..queries import add_action

from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


async def get_numbers(**kwargs):
    nums = [
        ("1️⃣", '1'),
        ("2️⃣", '2'),
        ("3️⃣", '3'),
        ("4️⃣", '4'),
        ("5️⃣", '5'),
    ]
    return {
        "nums": nums,
        "count": len(nums),
    }


async def get_last_user_on(users: RedisStorage, user_id: int) -> UserOnboarding:

    user_onboarding_raw = await users.redis.lrange(f"{user_id}_on", 0, -1)
    if user_onboarding_raw:
        return UserOnboarding.model_validate_json(user_onboarding_raw[0])

    return UserOnboarding()


async def get_last_user_off(users: RedisStorage, user_id: int) -> UserOffboarding:

    user_offboarding_raw = await users.redis.lrange(f"{user_id}_off", 0, -1)
    if user_offboarding_raw:
        return UserOffboarding.model_validate_json(user_offboarding_raw[0])
    
    return UserOffboarding()


# Callback handlers for the buttons
async def on_approve(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

    users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)

    user_oboarding: UserOnboarding = UserOnboarding(approve=True)
    await users.redis.lpush(f"{callback.from_user.id}_on", user_oboarding.model_dump_json(indent=4))
    await add_action(dialog_manager, Action.ONBOARDING)

    await dialog_manager.next()


# async def on_principe(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

#     users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
#     await add_action(dialog_manager, Action.ONBOARDING)

#     if not await users.redis.sismember("russian_names", callback.from_user.first_name):
#         await dialog_manager.next()
#     else:
#         await dialog_manager.switch_to(Onboarding.AGE)


# async def on_disapprove(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
#     await add_action(dialog_manager, Action.ONBOARDING)
#     await callback.message.answer("К сожалению, без согласия на обработку данных бот не сможет работать. "
#                                   "Если ты передумаешь, просто напиши /start.")


# # Хэндлер, который сработает, если пользователь ввел корректный возраст
# async def correct_name_handler(
#         message: Message, 
#         widget: ManagedTextInput, 
#         dialog_manager: DialogManager, 
#         text: str) -> None:
    
#     users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
#     user_oboarding: UserOnboarding = await get_last_user_on(users, message.from_user.id)

#     user_oboarding.name = text

#     await add_action(dialog_manager, Action.ONBOARDING)
#     await users.redis.lpush(f"{message.from_user.id}_on", user_oboarding.model_dump_json(indent=4))
#     await dialog_manager.next()


# # Проверка текста на то, что он содержит число от 16 до 45 включительно
# def age_check(text: str) -> str:
#     if all(ch.isdigit() for ch in text) and 16 <= int(text) <= 70:
#         return text
#     raise ValueError


# # Хэндлер, который сработает, если пользователь ввел корректный возраст
# async def correct_age_handler(
#         message: Message, 
#         widget: ManagedTextInput, 
#         dialog_manager: DialogManager, 
#         text: str) -> None:
    
#     users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
#     user_oboarding: UserOnboarding = await get_last_user_on(users, message.from_user.id)
#     await add_action(dialog_manager, Action.ONBOARDING)

#     user_oboarding.age = text

#     await users.redis.lpush(f"{message.from_user.id}_on", user_oboarding.model_dump_json(indent=4))

#     await dialog_manager.next()


# # Хэндлер, который сработает на ввод некорректного возраста
# async def error_age_handler(
#         message: Message, 
#         widget: ManagedTextInput, 
#         dialog_manager: DialogManager, 
#         error: ValueError):
#     await message.answer(
#         text='Вы ввели некорректный возраст. Попробуйте еще раз'
#     )


# async def handle_education(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

#     users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
#     user_oboarding: UserOnboarding = await get_last_user_on(users, callback.from_user.id)
#     await add_action(dialog_manager, Action.ONBOARDING)
    
#     user_oboarding.education = callback.data

#     await users.redis.lpush(f"{callback.from_user.id}_on", user_oboarding.model_dump_json(indent=4))
#     await dialog_manager.next()


# async def handle_status(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

#     users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
#     user_oboarding: UserOnboarding = await get_last_user_on(users, callback.from_user.id)
#     await add_action(dialog_manager, Action.ONBOARDING)
    
#     user_oboarding.current_status = callback.data
    
#     await users.redis.lpush(f"{callback.from_user.id}_on", user_oboarding.model_dump_json(indent=4))

#     if "staff" in callback.data:
#         await dialog_manager.switch_to(Onboarding.ABOUT)
#     else:
#         await dialog_manager.next()


# async def handle_university(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    
#     users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
#     user_oboarding: UserOnboarding = await get_last_user_on(users, callback.from_user.id)
#     await add_action(dialog_manager, Action.ONBOARDING)
    
#     user_oboarding.university = callback.data
    
#     await users.redis.lpush(f"{callback.from_user.id}_on", user_oboarding.model_dump_json(indent=4))
#     await dialog_manager.next()


# async def handle_about(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    
#     users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
#     user_oboarding: UserOnboarding = await get_last_user_on(users, callback.from_user.id)

#     user_oboarding.about = callback.data
#     await users.redis.lpush(f"{callback.from_user.id}_on", user_oboarding.model_dump_json(indent=4))

#     if "socials" in callback.data:
#         await dialog_manager.next()

#     else:
#         await dialog_manager.switch_to(Onboarding.PERSON)


# async def handle_clarify(
#     message: Message, 
#     widget: ManagedTextInput, 
#     dialog_manager: DialogManager, 
#     text: str) -> None:
    
#     users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
#     user_oboarding: UserOnboarding = await get_last_user_on(users, message.from_user.id)
#     await add_action(dialog_manager, Action.ONBOARDING)
    
#     user_oboarding.about = text
    
#     await users.redis.lpush(f"{message.from_user.id}_on", user_oboarding.model_dump_json(indent=4))
#     await dialog_manager.next()


# async def start_interaction(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
#     await add_action(dialog_manager, Action.ONBOARDING)

#     await dialog_manager.next()


# async def on_num_selected(
#         callback: CallbackQuery, 
#         widget: Any,
#         dialog_manager: DialogManager, 
#         item_id: str):
    
#     state: State = get_current_state(dialog_manager)
    
#     users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
#     user_oboarding: UserOnboarding = await get_last_user_on(users, callback.from_user.id)
    
#     match state:
#         case Onboarding.QUESTION_1:
#             user_oboarding.question_1 = item_id
#         case Onboarding.QUESTION_2:
#             user_oboarding.question_2 = item_id
#         case Onboarding.QUESTION_3:
#             user_oboarding.question_3 = item_id
#         case Onboarding.QUESTION_4:
#             user_oboarding.question_4 = item_id

#     await add_action(dialog_manager, Action.ONBOARDING)
    
#     await users.redis.lpush(f"{callback.from_user.id}_on", user_oboarding.model_dump_json(indent=4))
#     await dialog_manager.next()


# async def finish_dialog(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

#     await add_action(dialog_manager, Action.ONBOARDING)

#     await dialog_manager.next()


# # Callback handlers for the buttons
# async def on_ready(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

#     users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
#     user_offboarding: UserOffboarding = UserOffboarding(approve=True)

#     await add_action(dialog_manager, Action.OFFBOARDING)

#     await users.redis.lpush(f"{callback.from_user.id}_off", user_offboarding.model_dump_json(indent=4))
#     await dialog_manager.next()


# async def on_num_selected_off(
#         callback: CallbackQuery, 
#         widget: Any,
#         dialog_manager: DialogManager, 
#         item_id: str):
    
#     state: State = get_current_state(dialog_manager)

#     users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
#     user_offboarding: UserOffboarding = await get_last_user_off(users, callback.from_user.id)
    
#     match state:
#         case Offboarding.QUESTION_1:
#             user_offboarding.question_1 = item_id
#         case Offboarding.QUESTION_2:
#             user_offboarding.question_2 = item_id
#         case Offboarding.QUESTION_3:
#             user_offboarding.question_3 = item_id
#         case Offboarding.QUESTION_4:
#             user_offboarding.question_4 = item_id
    
#     await add_action(dialog_manager, Action.OFFBOARDING)

#     await users.redis.lpush(f"{callback.from_user.id}_off", user_offboarding.model_dump_json(indent=4))
#     await dialog_manager.next()


# # Хэндлер, который сработает, если пользователь ввел корректный возраст
# async def associate_handler(
#         message: Message, 
#         widget: ManagedTextInput, 
#         dialog_manager: DialogManager, 
#         text: str) -> None:
    
#     users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
#     user_offboarding: UserOffboarding = await get_last_user_off(users, message.from_user.id)

#     user_offboarding.associate = text

#     await add_action(dialog_manager, Action.OFFBOARDING)

#     await users.redis.lpush(f"{message.from_user.id}_off", user_offboarding.model_dump_json(indent=4))
#     await dialog_manager.next()


# # Callback handlers for the buttons
# async def on_skip(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):

#     i18n: TranslatorRunner = dialog_manager.middleware_data['i18n']

#     await add_action(dialog_manager, Action.OFFBOARDING)
#     await callback.message.answer(f"{i18n.offboarding.thanks_msg()}")


# async def feedback_handler(
#         message: Message, 
#         widget: ManagedTextInput, 
#         dialog_manager: DialogManager, 
#         text: str) -> None:
    
#     users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
#     user_offboarding: UserOffboarding = await get_last_user_off(users, message.from_user.id)

#     user_offboarding.feedback = text

#     await add_action(dialog_manager, Action.OFFBOARDING)

#     await users.redis.lpush(f"{message.from_user.id}_off", user_offboarding.model_dump_json(indent=4))
#     await dialog_manager.next()
