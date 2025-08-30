import asyncio
import os
from io import BytesIO
from typing import Optional, Tuple

import face_recognition

from aiogram.types import Message
from aiogram.enums import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput

from ..states import Onboarding

from .utils import get_middleware_data
from my_tools import get_datetime_now, DateTimeKeys


async def analyze_face_in_image(bot, file_id: str) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Analyzes a photo for face detection and quality.
    
    Returns:
        Tuple[bool, Optional[str], Optional[float]]: 
        - success: bool - whether the photo is suitable
        - error_message: Optional[str] - error message if photo is not suitable
        - face_ratio: Optional[float] - face to image ratio if photo is suitable
    """
    buf = BytesIO()
    
    try:
        await bot.download(file=file_id, destination=buf)
        buf.seek(0)
        
        image = face_recognition.load_image_file(buf)
        h, w = image.shape[:2]
        img_area = h * w

        face_locations = face_recognition.face_locations(image)
        
        if len(face_locations) == 0:
            return False, '😕 Лицо не найдено. Попробуйте фото, где лицо видно лучше.', None

        if len(face_locations) > 1:
            return False, '😕 Найдено несколько лиц. Попробуйте фото, где лицо видно лучше.', None

        (top, right, bottom, left) = face_locations[0]
        face_area = (right - left) * (bottom - top)
        
        if img_area == 0:
            return False, '⚠️ Не удалось определить размер изображения.', None
            
        face_ratio = face_area / img_area
        
        if face_ratio <= 0.15:
            return False, '⚠️ Лицо слишком маленькое (менее 15% кадра). Загрузите фото, где лицо крупнее.', None

        return True, None, face_ratio
        
    except Exception as e:
        return False, f'❌ Ошибка при обработке изображения: {str(e)}', None


async def handle_photo(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    bot, _, user_data = get_middleware_data(dialog_manager)
    date: str = get_datetime_now(DateTimeKeys.DEFAULT)

    if not message.photo:
        await message.answer(text='❗Это должна быть фотография')
        await asyncio.sleep(1)
        return

    success, error_message, _ = await analyze_face_in_image(bot, message.photo[-1].file_id)
    
    if not success:
        await message.answer(text=error_message)
        await asyncio.sleep(1)
        return

    # Save the photo
    await bot.download(
        file=message.photo[-1].file_id,
        destination=f"media/{user_data.id}/onboarding/profile_{date}.jpg"
    )

    await message.answer(text='✅ Фотография успешно загружена')

    await dialog_manager.switch_to(Onboarding.STEP_1)
