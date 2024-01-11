from typing import Optional, Callable, Any, Awaitable, cast

from aiogram import BaseMiddleware, Router, Bot
from aiogram.types import Message
from cachetools import TTLCache
from pyrogram import Client

from aiogram_album.base_message import BaseAlbumMessage
from aiogram_album.album_message import AlbumMessage
from aiogram_album.pyrogram_album.utls import to_message


class PyrogramAlbumMiddleware(BaseMiddleware):
    cache: TTLCache
    client: Client
    message_class: type[BaseAlbumMessage]

    @classmethod
    async def from_app_data(
            cls, /,
            bot_token: str,
            api_id: int,
            api_hash: str,
            name: Optional[str] = None,
            router: Optional[Router] = None,
            message_class: type[BaseAlbumMessage] = AlbumMessage,
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
            **kwargs
        )
        await client.start()
        return cls(
            client=client,
            router=router,
            message_class=message_class,
            maxsize=maxsize,
            ttl=ttl,
        )

    def __init__(
            self, /,
            client: Client,
            router: Optional[Router] = None,
            message_class: type[BaseAlbumMessage] = AlbumMessage,
            maxsize: Optional[int] = None,
            ttl: Optional[int] = None,
    ):
        self.client = client
        self.message_class = message_class
        self.cache = TTLCache(maxsize=maxsize or 100, ttl=ttl or 10)
        if router:
            router.message.outer_middleware.register(self)

    async def get_album(self, message: Message, bot: Bot) -> list[Message]:
        return [
            to_message(m, bot)
            for m in await self.client.get_media_group(
                chat_id=message.chat.id,
                message_id=message.message_id,
            )
        ]

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any],
    ) -> Any:
        if event.media_group_id:
            if event.media_group_id in self.cache:
                return
            self.cache[event.media_group_id] = True
            data["__pyro"] = self.client
            event = self.message_class.new(
                messages=await self.get_album(
                    message=event,
                    bot=cast(Bot, data["bot"]),
                ),
                data=data
            )
            data.pop("__pyro", None)
        return await handler(event, data)
