import asyncio
from typing import Any, Callable, Dict, Awaitable, Union, Optional, MutableMapping

from aiogram import BaseMiddleware, Router
from aiogram.types import Message
from cachetools import TTLCache

from aiogram_album import AlbumMessage


class LockAlbumMiddleware(BaseMiddleware):
    cache: MutableMapping[str, list[Message]]

    def __init__(
            self,
            latency: Union[int, float] = 0.2,
            maxsize: int = 1000,
            ttl: Union[int, float] = 10,
            router: Optional[Router] = None,
    ):
        self.lock = asyncio.Lock()
        self.latency = latency
        self.cache = TTLCache(maxsize=maxsize, ttl=float(ttl) + 20.0)
        if router:
            router.message.outer_middleware(self)

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        if event.media_group_id is None:
            return await handler(event, data)

        album_id: str = event.media_group_id

        async with self.lock:
            self.cache.setdefault(album_id, list())
            self.cache[album_id].append(event)

        # Wait for some time until other updates are collected
        await asyncio.sleep(self.latency)

        # Find the smallest message_id in batch, this will be our only update
        # which will pass to handlers
        my_message_id = smallest_message_id = event.message_id

        for item in self.cache[album_id]:
            smallest_message_id = min(smallest_message_id, item.message_id)

        # If current message_id in not the smallest, drop the update;
        # it's already saved in self.albums_cache
        if my_message_id != smallest_message_id:
            return

        event = AlbumMessage.new(
            messages=self.cache[album_id],
            data=data
        )

        return await handler(event, data)
