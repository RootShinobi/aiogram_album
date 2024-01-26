from asyncio import sleep
from typing import Union, Optional, Any, List, Dict

from aiogram import Dispatcher
from aiogram.types import Message

from .album_message import AlbumMessage
from .base_middleware import BaseAlbumMiddleware


class WithoutCountCheckAlbumMiddleware(BaseAlbumMiddleware):
    def __init__(
        self,
        latency: Union[int, float] = 0.1,
        dispatcher: Optional[Dispatcher] = None,
    ):
        super().__init__(dispatcher=dispatcher)
        self.latency = latency
        self.album_data: Dict[str, List[Message]] = {}

    async def handle(
        self,
        message: Message,
        data: Dict[str, Any],
    ) -> Optional[AlbumMessage]:
        try:
            self.album_data[message.media_group_id].append(message)
            return
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await sleep(self.latency)
            album_message = AlbumMessage.new(
                messages=self.album_data.pop(message.media_group_id), data=data
            )

        return album_message
