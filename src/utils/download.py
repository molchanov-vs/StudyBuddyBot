import logging

import zipfile
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from aiogram.types import CallbackQuery
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import FSInputFile

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button


from my_tools import get_users

from ..custom_types import UserData, UserOnboarding, UserOffboarding
from ..enums import Database

from ..utils.utils import get_middleware_data


async def download_user_info(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    bot, config, _ = get_middleware_data(dialog_manager)
    users: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
    now: datetime = datetime.now(ZoneInfo(config.system.time_zone))
    current_date = now.date().isoformat()
    
    # Create a temporary directory for files in Docker container
    temp_dir = Path(f"/app/media/temp_user_files_{now.timestamp()}")
    temp_dir.mkdir(exist_ok=True)
    
    known_users: list[int] = await get_users(users, [])
    
    for user_id in known_users:
        try:
            # Get first element from user's list
            user_data = await users.redis.lindex(f"{user_id}", 0)

            # Get onboarding data
            onboarding_data = await users.redis.lindex(f"{user_id}_on", 0)
            
            # Get message history
            message_history = await users.redis.lrange(f"{user_id}_h", 0, -1)

            # Get offboarding data
            offboarding_data = await users.redis.lindex(f"{user_id}_off", 0)
            
            # Create text file for user
            file_path = temp_dir / f"{user_id}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                
                f.write("User Data:\n")
                if user_data:
                    f.write(f"User Data:\n{UserData.model_validate_json(user_data).model_dump_json(indent=4)}\n\n")

                f.write("\nOnboarding:\n")
                if onboarding_data:
                    f.write(f"{UserOnboarding.model_validate_json(onboarding_data).model_dump_json(indent=4)}\n\n")

                f.write("\nMessage History:\n")
                for msg in message_history[::-1]:
                    f.write(f"{msg.decode('utf-8')}\n")

                f.write("\nOffboarding:\n")
                if offboarding_data:
                    f.write(f"{UserOffboarding.model_validate_json(offboarding_data).model_dump_json(indent=4)}\n\n")
            
            logging.info(f"Created file for user {user_id} on {current_date}")
            
        except Exception as e:
            logging.error(f"Error processing user {user_id}: {str(e)}")
            continue
    
    # Create zip file
    zip_path = Path(f"user_data_{now.replace(tzinfo=None).isoformat(timespec='seconds')}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in temp_dir.glob("*.txt"):
            zipf.write(file, file.name)
    
    # Clean up temporary directory
    for file in temp_dir.glob("*.txt"):
        file.unlink()
    temp_dir.rmdir()
    
    # Send zip file to the user who triggered the download
    try:
        await bot.send_document(
            chat_id=callback.from_user.id,
            document=FSInputFile(zip_path),
            caption=f"User data archive created",
            message_effect_id=config.message_effect.fire

        )
        zip_path.unlink()  # Remove zip file after sending

    except Exception as e:
        logging.error(f"Error sending zip file: {str(e)}")
        await callback.answer("Error creating or sending the archive", show_alert=True)