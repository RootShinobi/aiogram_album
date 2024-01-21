from typing import List, Union, Optional

from aiogram.types import (
    MessageId,
)
from aiogram.types.base import UNSET_PROTECT_CONTENT

try:
    from aiogram.methods import DeleteMessages, ForwardMessages, CopyMessages
except ImportError:
    from aiogram_album.methods import DeleteMessages, ForwardMessages, CopyMessages

from .base_message import BaseAlbumMessage


class AlbumMessage(BaseAlbumMessage):
    async def copy_to(
        self,
        chat_id: Union[int, str],
        message_thread_id: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = UNSET_PROTECT_CONTENT,
        remove_caption: Optional[bool] = None,
        request_timeout: Optional[int] = None,
    ) -> List[MessageId]:
        return await self.bot(
            CopyMessages(
                chat_id=chat_id,
                from_chat_id=self.chat.id,
                message_ids=self.message_ids,
                message_thread_id=message_thread_id,
                disable_notification=disable_notification,
                protect_content=protect_content,
                remove_caption=remove_caption,
                request_timeout=request_timeout,
            )
        )

    async def delete(
        self,
        request_timeout: Optional[int] = None,
    ) -> bool:
        return await self.bot(
            DeleteMessages(
                chat_id=self.chat.id,
                message_ids=self.message_ids,
                request_timeout=request_timeout,
            )
        )

    async def forward(
        self,
        chat_id: Union[int, str],
        message_thread_id: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = UNSET_PROTECT_CONTENT,
        request_timeout: Optional[int] = None,
    ) -> List[MessageId]:
        return await self.bot(
            ForwardMessages(
                chat_id=chat_id,
                from_chat_id=self.chat.id,
                message_thread_id=message_thread_id,
                message_ids=self.message_ids,
                disable_notification=disable_notification,
                protect_content=protect_content,
                request_timeout=request_timeout,
            )
        )
