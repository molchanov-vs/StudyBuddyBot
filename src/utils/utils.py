from typing import TYPE_CHECKING, Literal

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


AFTER_MESSAGES = messages = [
    "Спасибо за твои ответы 🙌 Сейчас мы оформляем галерею студентов и преподавателей. Как только всё будет готово, я обязательно дам знать!",
    "Мы уже получили твои материалы. Сейчас собираем общую галерею, и как только её опубликуем — я сразу напишу тебе!",
    "Благодарю за твои ответы 🌿 Мы работаем над созданием галереи студентов и преподавателей. Как только она будет доступна, я поделюсь ссылкой.",
    "Твои ответы уже у нас 👌 Сейчас идёт подготовка галереи. Чуть позже я пришлю тебе обновление, когда всё будет готово.",
    "Спасибо, что откликнулся. Мы уже собираем галерею, и как только её доделаем, я сразу свяжусь с тобой!"
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

    want: str = dialog_manager.dialog_data.get("gender", "unknown")

    want = "хотел" if want == "male" else "хотела" if want == "female" else "хотел(а)"

    return {
        "back_btn": i18n.service.back_btn(),
        "next_btn": i18n.service.next_btn(),
        "welcome": i18n.onboarding.welcome(),
        "super_btn": i18n.onboarding.super_btn(),
        "preonboarding": i18n.onboarding.preonboarding(),
        "approve_btn": i18n.onboarding.approve_btn(),
        "disapprove_btn": i18n.onboarding.disapprove_btn(),
        "name": i18n.onboarding.name(),
        "important_today": i18n.onboarding.important_today(),
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


def determine_russian_name_gender(full_name: str) -> Literal["male", "female", "unknown"]:
    """
    Determine the gender of a Russian name by analyzing both first name and surname.
    
    Args:
        full_name: Full name in format "FirstName LastName" (e.g., "Иван Петров" or "Мария Иванова")
    
    Returns:
        "male", "female", or "unknown" if gender cannot be determined
    """
    if not full_name or not isinstance(full_name, str):
        return "unknown"
    
    words = full_name.strip().split()
    if len(words) != 2:
        return "unknown"
    
    first_name, surname = words[0].lower(), words[1].lower()
    
    # Male first names (common Russian male names)
    male_names = {
        'александр', 'алексей', 'андрей', 'артём', 'артем', 'владимир', 'владислав',
        'дмитрий', 'евгений', 'иван', 'игорь', 'константин', 'максим', 'михаил',
        'николай', 'павел', 'петр', 'пётр', 'сергей', 'станислав', 'степан', 'стефан',
        'тимофей', 'фёдор', 'федор', 'юрий', 'ярослав', 'антон', 'василий', 'виктор',
        'григорий', 'даниил', 'данил', 'денис', 'егор', 'кирилл', 'леонид', 'матвей',
        'назар', 'олег', 'роман', 'святослав', 'семён', 'семен', 'тимур', 'филипп',
        'эдуард', 'яков', 'арсений', 'богдан', 'валентин', 'валерий', 'всеволод',
        'георгий', 'герман', 'глеб', 'давид', 'демьян', 'захар', 'илья', 'иннокентий',
        'карл', 'леонтий', 'лука', 'марк', 'мирон', 'нестор', 'порфирий', 'прохор',
        'рафаил', 'савва', 'савелий', 'самсон', 'севастьян', 'сидор', 'сила',
        'сильвестр', 'спиридон', 'трофим', 'устин', 'фома', 'эммануил', 'эраст'
    }
    
    # Female first names (common Russian female names)
    female_names = {
        'александра', 'алёна', 'алена', 'алина', 'алла', 'анна', 'ангелина',
        'анжела', 'анжелика', 'антонина', 'валентина', 'валерия', 'варвара',
        'вера', 'вероника', 'виктория', 'галина', 'дарья', 'диана', 'евгения',
        'екатерина', 'елена', 'елизавета', 'елизавета', 'жанна', 'зинаида',
        'зоя', 'инна', 'ирина', 'карина', 'кира', 'клавдия', 'ксения', 'лариса',
        'лидия', 'любовь', 'людмила', 'марина', 'мария', 'маргарита', 'надежда',
        'наталья', 'наталия', 'нина', 'оксана', 'ольга', 'полина', 'раиса',
        'регина', 'римма', 'светлана', 'софья', 'софия', 'тамара', 'татьяна',
        'ульяна', 'юлия', 'яна', 'анжелика', 'антонина', 'василиса', 'вера',
        'вероника', 'галина', 'дарья', 'диана', 'евдокия', 'евфросиния',
        'екатерина', 'елена', 'елизавета', 'ефросинья', 'жанна', 'зинаида',
        'зоя', 'инна', 'ирина', 'карина', 'кира', 'клавдия', 'ксения', 'лариса',
        'лидия', 'любовь', 'людмила', 'марина', 'мария', 'маргарита', 'надежда',
        'наталья', 'нина', 'оксана', 'ольга', 'полина', 'раиса', 'регина',
        'римма', 'светлана', 'софья', 'софия', 'тамара', 'татьяна', 'ульяна',
        'юлия', 'яна', 'ангелина', 'анжела', 'анжелика', 'антонина', 'василиса',
        'вера', 'вероника', 'галина', 'дарья', 'диана', 'евдокия', 'евфросиния',
        'екатерина', 'елена', 'елизавета', 'ефросинья', 'жанна', 'зинаида',
        'зоя', 'инна', 'ирина', 'карина', 'кира', 'клавдия', 'ксения', 'лариса',
        'лидия', 'любовь', 'людмила', 'марина', 'мария', 'маргарита', 'надежда',
        'наталья', 'нина', 'оксана', 'ольга', 'полина', 'раиса', 'регина',
        'римма', 'светлана', 'софья', 'софия', 'тамара', 'татьяна', 'ульяна',
        'юлия', 'яна'
    }
    
    # Check first name first (most reliable indicator)
    if first_name in male_names:
        return "male"
    elif first_name in female_names:
        return "female"
    
    # If first name is not in our lists, check surname endings
    # Male surname endings
    male_endings = ['ов', 'ев', 'ин', 'ын', 'ой', 'ий', 'ой', 'ский', 'цкий', 'ской', 'цкой']
    # Female surname endings (same as male but with 'а' at the end)
    female_endings = ['ова', 'ева', 'ина', 'ына', 'ая', 'ая', 'ая', 'ская', 'цкая', 'ская', 'цкая']
    
    # Check surname endings
    for ending in male_endings:
        if surname.endswith(ending):
            return "male"
    
    for ending in female_endings:
        if surname.endswith(ending):
            return "female"
    
    # Additional checks for common patterns
    # Names ending with 'а' are often female
    if first_name.endswith('а') and not first_name.endswith('ия'):
        return "female"
    
    # Names ending with 'й' are often male
    if first_name.endswith('й'):
        return "male"
    
    # Names ending with 'ь' can be either, but often male
    if first_name.endswith('ь'):
        return "male"
    
    return "unknown"