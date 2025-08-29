from typing import TYPE_CHECKING

import os
import re

from aiogram import Bot
from aiogram.types import User
from aiogram.fsm.state import State
from aiogram_dialog import DialogManager

from my_tools import DialogManagerKeys

from ..custom_types import UserData
from ..config import Config

from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


SORRY_MESSAGES = [
    "К сожалению, я не смогла ответить на ваше сообщение. Попробуйте перефразировать его.",
    "Извините, но я не совсем поняла ваше сообщение. Не могли бы вы сформулировать его по-другому?",
    "Мне трудно понять, что вы имеете в виду. Может быть, попробуете объяснить иначе?",
    "Прошу прощения, но мне нужно, чтобы вы выразили свою мысль немного иначе.",
    "Кажется, произошла небольшая путаница. Давайте попробуем сформулировать вопрос по-другому?",
    "Не могу корректно обработать ваше сообщение. Пожалуйста, перефразируйте его.",
    "Извините за неудобство, но не могли бы вы выразить свою мысль другими словами?",
    "У меня возникли сложности с пониманием вашего сообщения. Попробуйте написать его иначе.",
    "К сожалению, я не могу дать подходящий ответ. Может быть, вы сможете переформулировать?",
    "Простите, но мне нужно, чтобы вы написали это сообщение другим способом."
]


def markdown_to_html(text: str) -> str:
    """
    Converts simplified Markdown-style formatting to Telegram HTML.
    Supports: **bold**, *italic*, _italic_, `code`, ```pre```.
    """
    # Bold: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text, flags=re.DOTALL)
    
    # Italic: *text* or _text_ (avoid matching inside bold)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text, flags=re.DOTALL)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<i>\1</i>', text, flags=re.DOTALL)
    
    # Inline code: `code`
    text = re.sub(r'`([^`\n]+?)`', r'<code>\1</code>', text)
    
    # Preformatted block (optional)
    # text = re.sub(r'```(.+?)```', r'<pre>\1</pre>', text, flags=re.DOTALL)

    return text


def get_middleware_data(dialog_manager: DialogManager) -> tuple[Bot, Config, UserData]:

    bot: Bot = dialog_manager.middleware_data[DialogManagerKeys.BOT]
    config: Config = dialog_manager.middleware_data.get(DialogManagerKeys.CONFIG)
    event_from_user: User = dialog_manager.middleware_data.get(DialogManagerKeys.EVENT_FROM_USER)
    user_data: UserData = UserData(**event_from_user.model_dump())

    return bot, config, user_data


def get_current_state(dialog_manager: DialogManager) -> State:

    return dialog_manager.current_context().state


def remove_logs():
    
    logs = sorted(os.listdir('logs'))

    if len(logs) > 5:
        for log in logs[:-1]:
            os.remove(f"logs/{log}")


def load_locales(
    i18n: TranslatorRunner,
    dialog_manager: DialogManager
    ) -> dict[str, str]:

    name: str = dialog_manager.dialog_data.get("name", "None")
    want: str = dialog_manager.dialog_data.get("want", "хотел(а)")

    return {
        "back_btn": i18n.service.back_btn(),
        "next_btn": i18n.service.next_btn(),
        "welcome": i18n.onboarding.welcome(),
        "super_btn": i18n.onboarding.super_btn(),
        "preonboarding": i18n.onboarding.preonboarding(),
        "approve_btn": i18n.onboarding.approve_btn(),
        "disapprove_btn": i18n.onboarding.disapprove_btn(),
        "name": i18n.onboarding.name(),
        "important_today": i18n.onboarding.important_today(name=name),
        "difficult_today": i18n.onboarding.difficult_today(),
        "something_else": i18n.onboarding.something_else(),
        "to_profile_btn": i18n.onboarding.to_profile_btn(),
        "no_photo": i18n.onboarding.no_photo(),
        "yes_photo": i18n.onboarding.yes_photo(),
        "yes_btn": i18n.onboarding.yes_btn(),
        "step_1": i18n.onboarding.step_1(),
        "background": i18n.onboarding.background(),
        "after_step_1": i18n.onboarding.after_step_1(),
        "step_2": i18n.onboarding.step_2(),
        "after_step_2": i18n.onboarding.after_step_2(),
        "step_3": i18n.onboarding.step_3(),
        "step_4": i18n.onboarding.step_4(want=want),
        "after_step_4": i18n.onboarding.after_step_4(),
        "step_5": i18n.onboarding.step_5(),
        "step_6": i18n.onboarding.step_6(),
        "thanks_btn": i18n.onboarding.thanks_btn(),
    }