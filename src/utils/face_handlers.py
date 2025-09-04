import logging
import os
from io import BytesIO
from typing import Optional, Tuple

from aiogram import Bot
import httpx

# Try to import local face_recognition library if available
try:
    import face_recognition  # type: ignore
except Exception:
    face_recognition = None  # Fallback to HTTP service in dev


async def analyze_face_in_image(
    bot: Bot, 
    file_id: str,
    user_id: int) -> Tuple[bool, Optional[str], Optional[float]]:
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
        face_service_url = os.getenv("FACE_RECOGNITION_URL")

        if face_recognition is not None and not face_service_url:
            # Local processing using face_recognition library
            image = face_recognition.load_image_file(buf)
            h, w = image.shape[:2]
            img_area = h * w

            face_locations = face_recognition.face_locations(image)

            if len(face_locations) == 0:
                logging.error(f"Face not found in image: {file_id} for user: {user_id}")
                return False, '😕 Лицо не найдено. Попробуйте фото, где лицо видно лучше.', None

            if len(face_locations) > 1:
                logging.error(f"Multiple faces found in image: {file_id} for user: {user_id}")
                return False, '😕 Найдено несколько лиц. Попробуйте фото, где лицо видно лучше.', None

            (top, right, bottom, left) = face_locations[0]
            face_area = (right - left) * (bottom - top)

            if img_area == 0:
                logging.error(f"Image area is 0 in image: {file_id} for user: {user_id}")
                return False, '⚠️ Не удалось определить размер изображения.', None

            face_ratio = face_area / img_area

            if face_ratio <= 0.10:
                logging.error(f"Face ratio is too small: {face_ratio} in image: {file_id} for user: {user_id}")
                return False, '⚠️ Лицо слишком маленькое (менее 10% кадра). Пожалуйста, загрузи фото, где лицо крупнее.', None

            return True, None, face_ratio
        else:
            # HTTP fallback to face recognition microservice
            if not face_service_url:
                logging.error("FACE_RECOGNITION_URL is not set and face_recognition is unavailable")
                return False, '❌ Сервис распознавания лиц недоступен в режиме разработки.', None

            buf.seek(0)
            files = {"file": (f"{file_id}.jpg", buf.getvalue(), "image/jpeg")}
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(f"{face_service_url}/analyze", files=files)
                data = resp.json()

            if not data.get("success"):
                error = data.get("error") or 'Неизвестная ошибка сервиса'
                # Map to localized messages similar to local flow
                if error == "Face not found":
                    return False, '😕 Лицо не найдено. Попробуйте фото, где лицо видно лучше.', None
                if error == "Multiple faces found":
                    return False, '😕 Найдено несколько лиц. Попробуйте фото, где лицо видно лучше.', None
                if error.startswith("Face too small"):
                    return False, '⚠️ Лицо слишком маленькое (менее 10% кадра). Пожалуйста, загрузи фото, где лицо крупнее.', data.get("face_ratio")
                return False, f'❌ Ошибка сервиса распознавания лиц: {error}', None

            return True, None, float(data.get("face_ratio", 0))
        
    except Exception as e:
        return False, f'❌ Ошибка при обработке изображения: {str(e)}', None
