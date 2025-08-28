from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, TelegramObject

from src.enums import Database


class RedisStorageMiddleware(BaseMiddleware):
    
    def __init__(self, storage: RedisStorage, db_name: Database):
        self.storage = storage
        self.db_name = db_name

    async def __call__(self, 
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: Message, 
                       data: Dict[str, Any]) -> Any:
        
        data[self.db_name.value] = self.storage

        return await handler(event, data)