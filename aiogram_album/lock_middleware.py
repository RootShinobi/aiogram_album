import asyncio
from typing import Any, Dict, Union, Optional, MutableMapping, List

from aiogram import Dispatcher
from aiogram.types import Message
from cachetools import TTLCache

from .album_message import AlbumMessage
from .base_middleware import BaseAlbumMiddleware


class LockAlbumMiddleware(BaseAlbumMiddleware):
    cache: MutableMapping[str, List[Message]]

    def __init__(
        self,
        latency: Union[int, float] = 0.2,
        maxsize: int = 1000,
        ttl: Union[int, float] = 10,
        dispatcher: Optional[Dispatcher] = None,
    ):
        super().__init__(dispatcher=dispatcher)
        self.lock = asyncio.Lock()
        self.latency = latency
        self.cache = TTLCache(maxsize=maxsize, ttl=float(ttl) + 20.0)

    async def handle(
        self,
        message: Message,
        data: Dict[str, Any],
    ) -> Optional[AlbumMessage]:
        album_id: str = message.media_group_id

        async with self.lock:
            self.cache.setdefault(album_id, list())
            self.cache[album_id].append(message)

        # Wait for some time until other updates are collected
        await asyncio.sleep(self.latency)

        # Find the smallest message_id in batch, this will be our only update
        # which will pass to handlers
        my_message_id = smallest_message_id = message.message_id

        for item in self.cache[album_id]:
            smallest_message_id = min(smallest_message_id, item.message_id)

        # If current message_id in not the smallest, drop the update;
        # it's already saved in self.albums_cache
        if my_message_id != smallest_message_id:
            return

        return AlbumMessage.new(messages=self.cache[album_id], data=data)
