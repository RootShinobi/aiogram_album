from typing import Union, Optional, List, cast, Any

from aiogram import Bot
from aiogram.types import Message
from pyrogram import Client
from pyrogram.types import Message as PyroMessage

from aiogram_album.base_message import BaseAlbumMessage
from aiogram_album.pyrogram_album.utls import to_message


class AlbumMessage(BaseAlbumMessage):
    _client: Client

    @classmethod
    def new(cls, messages: List[Message], data: dict[str, Any]) -> "AlbumMessage":
        client = cast(Client, data["__pyro"])
        bot = cast(Bot, data["bot"])
        return cls.new_data(
            messages=messages,
            client=client,
            bot=bot,
        )

    @classmethod
    def new_data(cls, messages: List[Message], client: Client, bot: Bot) -> "AlbumMessage":
        self = cls.model_validate(messages[0], from_attributes=True).as_(bot)
        self._messages = messages
        self._client = client
        setattr(self, messages[0].content_type, None)
        return self

    @classmethod
    def _from_pyro_messages(
            cls,
            messages: List[PyroMessage],
            client: Client,
            bot: Bot
    ) -> "AlbumMessage":
        return cls.new_data(
            messages=[to_message(message=message, bot=bot) for message in messages],
            client=client,
            bot=bot,
        )

    async def forward(
            self,
            chat_id: Union[int, str],
            disable_notification: Optional[bool] = None,
            protect_content: Optional[bool] = None,
            to_album: bool = False,
    ) -> "AlbumMessage":
        return AlbumMessage._from_pyro_messages(
            messages=await self._client.forward_messages(
                chat_id=chat_id,
                from_chat_id=self.chat.id,
                message_ids=self.message_ids,
                disable_notification=disable_notification,
                protect_content=protect_content,
            ),
            client=self._client,
            bot=self.bot,
        )

    async def delete(self) -> int:
        return await self._client.delete_messages(
            chat_id=self.chat.id,
            message_ids=self.message_ids,
        )

    async def copy_to(
            self,
            chat_id: Union[int, str],
            message_thread_id: Optional[int] = None,
            caption: Optional[Union[List[str], str]] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            to_album: bool = False,
    ) -> "AlbumMessage":
        return AlbumMessage._from_pyro_messages(
            messages=await self._client.copy_media_group(
                chat_id=chat_id,
                from_chat_id=self.chat.id,
                message_id=self.message_id,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
            ),
            client=self._client,
            bot=self.bot,
        )
