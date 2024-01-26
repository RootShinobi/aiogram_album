from asyncio import sleep
from typing import Union, Optional, Any, Dict

from aiogram import Dispatcher
from aiogram.types import Message
from cachetools import TTLCache

from .album_message import AlbumMessage
from .base_middleware import BaseAlbumMiddleware


class TTLCacheAlbumMiddleware(BaseAlbumMiddleware):
    def __init__(
        self,
        latency: Union[int, float] = 0.2,
        maxsize: int = 10000,
        ttl: int = 10,
        dispatcher: Optional[Dispatcher] = None,
    ):
        super().__init__(dispatcher=dispatcher)
        self.latency = latency
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    async def handle(
        self,
        message: Message,
        data: Dict[str, Any],
    ) -> Optional[AlbumMessage]:
        try:
            self.cache[message.media_group_id].append(message)
            return
        except KeyError:
            self.cache[message.media_group_id] = [message]
            await sleep(self.latency)
            album_message = AlbumMessage.new(
                messages=self.cache.pop(message.media_group_id), data=data
            )

        return album_message
