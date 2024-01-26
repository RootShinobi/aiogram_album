from typing import Optional, Any, cast, Dict, List, Type

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from cachetools import TTLCache
from pyrogram import Client

from aiogram_album.album_message import AlbumMessage
from aiogram_album.base_message import BaseAlbumMessage
from aiogram_album.base_middleware import BaseAlbumMiddleware
from aiogram_album.pyrogram_album.utls import to_message


class PyrogramAlbumMiddleware(BaseAlbumMiddleware):
    cache: TTLCache
    client: Client
    message_class: Type[BaseAlbumMessage]

    @classmethod
    async def from_app_data(
        cls,
        /,
        bot_token: str,
        api_id: int,
        api_hash: str,
        name: Optional[str] = None,
        dispatcher: Optional[Dispatcher] = None,
        message_class: Type[BaseAlbumMessage] = AlbumMessage,
        maxsize: Optional[int] = None,
        ttl: Optional[int] = None,
        **kwargs,
    ):
        client = Client(
            bot_token=bot_token,
            name=name or str(bot_token.split(":")[0]),
            api_id=api_id,
            api_hash=api_hash,
            no_updates=kwargs.pop("no_updates", True),
            **kwargs,
        )
        await client.start()
        return cls(
            client=client,
            dispatcher=dispatcher,
            message_class=message_class,
            maxsize=maxsize,
            ttl=ttl,
        )

    def __init__(
        self,
        /,
        client: Client,
        dispatcher: Optional[Dispatcher] = None,
        message_class: Type[BaseAlbumMessage] = AlbumMessage,
        maxsize: Optional[int] = None,
        ttl: Optional[int] = None,
    ):
        super().__init__(dispatcher=dispatcher)
        self.client = client
        self.message_class = message_class
        self.cache = TTLCache(maxsize=maxsize or 100, ttl=ttl or 10)

    async def get_album(self, message: Message, bot: Bot) -> List[Message]:
        return [
            to_message(m, bot)
            for m in await self.client.get_media_group(
                chat_id=message.chat.id,
                message_id=message.message_id,
            )
        ]

    async def handle(
        self,
        message: Message,
        data: Dict[str, Any],
    ) -> Optional[AlbumMessage]:
        if message.media_group_id in self.cache:
            return
        self.cache[message.media_group_id] = True
        data["__pyro"] = self.client
        album_message = self.message_class.new(
            messages=await self.get_album(
                message=message,
                bot=cast(Bot, data["bot"]),
            ),
            data=data,
        )
        data.pop("__pyro", None)
        return album_message
