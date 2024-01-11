import asyncio
from typing import Any, Dict, Union, Callable, Awaitable, Optional

from aiogram import BaseMiddleware, Router
from aiogram.types import Message

from aiogram_album.album_message import AlbumMessage


class CountCheckAlbumMiddleware(BaseMiddleware):
    def __init__(
            self,
            latency: Union[int, float] = 0.1,
            router: Optional[Router] = None,
    ):
        self.latency = latency
        self.album_data: dict[str, list[Message]] = {}
        if router:
            router.message.outer_middleware(self)

    def collect_album_messages(self, event: Message):
        if event.media_group_id not in self.album_data:
            self.album_data[event.media_group_id] = list()
        self.album_data[event.media_group_id].append(event)
        return len(self.album_data[event.media_group_id])

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if event.media_group_id is None:
            return await handler(event, data)
        total_before = self.collect_album_messages(event)
        await asyncio.sleep(self.latency)
        total_after = len(self.album_data[event.media_group_id])
        if total_before != total_after:
            return
        event = AlbumMessage.new(
            messages=self.album_data.pop(event.media_group_id),
            data=data
        )
        # album_messages.sort(key=lambda x: x.message_id)
        return await handler(event, data)
