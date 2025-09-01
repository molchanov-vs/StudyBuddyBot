import logging

from aiogram_dialog import DialogManager
from aiogram.fsm.storage.redis import RedisStorage

from .enums import Database, Action, RedisKeys
from .custom_types import UserAction, UserData

from .utils.utils import get_middleware_data


async def add_action(
        dialog_manager: DialogManager,
        action: str = None,
        user_data: UserData | None = None
) -> None:

    if not user_data:
        _, _, user_data = get_middleware_data(dialog_manager)

    if not action:
        current_state = dialog_manager.current_context().state
        action = current_state.state

    users_storage: RedisStorage = dialog_manager.middleware_data.get(Database.USERS)
    
    await push_action(action, user_data, users_storage)

    if action.startswith(tuple([Action.START, Action.RESTART])):

        await users_storage.redis.sadd(RedisKeys.KNOWN_USERS, user_data.id)

        current_profile: UserData | None = await get_current_profile(users_storage, user_data)
        user_data_json = user_data.model_dump_json(indent=4)

        if current_profile is None or current_profile != user_data:
            try:
                await users_storage.redis.lpush(user_data.id, user_data_json)
            except Exception as e:
                logging.error(f"Error updating profile for user {user_data.id} ({user_data.full_name}):\n{e}")


async def push_action(
        action: str, 
        user_data: UserData, 
        users_storage: RedisStorage
        ) -> None:
    
    """
    Pushes a user action to the Redis list.
    
    Args:
        action (str): The action identifier.
        user_data (UserData): The user's data.
        users_storage (RedisStorage): The Redis storage interface.
    """

    user_action: UserAction = UserAction(action_id=action)
    user_action_json = user_action.model_dump_json(indent=4)

    try:
        await users_storage.redis.lpush(f"{user_data.id}_a", user_action_json)

    except Exception as e:
        logging.error(f"Error pushing action for user {user_data.id} ({user_data.full_name})):\n{e}")


async def get_current_profile(
    users_storage: RedisStorage,
    user_data: UserData
    ) -> UserData | None:
    """
    Retrieves and validates the current profile for a user from Redis.
    
    Args:
        users_storage (RedisStorage): The Redis storage interface.
        user_data (UserData): The user's data.
    
    Returns:
        UserData | None: The validated user profile or None if not found or invalid.
    """

    current_profile_raw = await users_storage.redis.lindex(user_data.id, 0)

    if not current_profile_raw:
        return None
    
    try:
        current_profile: UserData = UserData.model_validate_json(current_profile_raw)
    
    except Exception as e:
        logging.warning(f"Validation error for user {user_data.id}:\n{e}")
        logging.warning(f"Can't validate raw json\n{current_profile_raw}")

        current_profile = None

    return current_profile