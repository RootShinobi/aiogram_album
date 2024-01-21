from asyncio import sleep
from typing import Union, Optional, Callable, Any, Awaitable

from aiogram import BaseMiddleware, Router
from aiogram.types import Message, TelegramObject
from cachetools import TTLCache

from aiogram_album.album_message import AlbumMessage


class TTLCacheAlbumMiddleware(BaseMiddleware):
    def __init__(
        self,
        latency: Union[int, float] = 0.2,
        maxsize: int = 10000,
        ttl: int = 10,
        router: Optional[Router] = None,
    ):
        self.latency = latency
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        if router:
            router.message.outer_middleware(self)
            router.channel_post.outer_middleware(self)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if not event.media_group_id:
            return await handler(event, data)

        try:
            self.cache[event.media_group_id].append(event)
            return
        except KeyError:
            self.cache[event.media_group_id] = [event]
            await sleep(self.latency)
            event = AlbumMessage.new(
                messages=self.cache.pop(event.media_group_id), data=data
            )

        return await handler(event, data)
