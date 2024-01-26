import asyncio
from typing import Any, Dict, Union, Optional, List

from aiogram import Dispatcher
from aiogram.types import Message

from aiogram_album.album_message import AlbumMessage
from .base_middleware import BaseAlbumMiddleware


class CountCheckAlbumMiddleware(BaseAlbumMiddleware):
    def __init__(
        self,
        latency: Union[int, float] = 0.1,
        dispatcher: Optional[Dispatcher] = None,
    ):
        super().__init__(dispatcher=dispatcher)
        self.latency = latency
        self.album_data: Dict[str, List[Message]] = {}

    def collect_album_messages(self, event: Message):
        if event.media_group_id not in self.album_data:
            self.album_data[event.media_group_id] = list()
        self.album_data[event.media_group_id].append(event)
        return len(self.album_data[event.media_group_id])

    async def handle(
        self,
        message: Message,
        data: Dict[str, Any],
    ) -> Optional[AlbumMessage]:
        total_before = self.collect_album_messages(message)
        await asyncio.sleep(self.latency)
        total_after = len(self.album_data[message.media_group_id])
        if total_before != total_after:
            return
        album_message = AlbumMessage.new(
            messages=self.album_data.pop(message.media_group_id), data=data
        )
        # album_messages.sort(key=lambda x: x.message_id)
        return album_message
