from itertools import zip_longest
from typing import Optional, List, Union, Iterator, Any, Dict, cast

from aiogram import Bot
from aiogram.types import (
    Message,
    UNSET_PARSE_MODE,
    InputMedia,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAudio,
    InputMediaDocument,
    MessageEntity,
)
from aiogram.types.base import UNSET


def to_input_media(
    message: Message,
    caption: Optional[str] = None,
    parse_mode: Optional[str] = UNSET_PARSE_MODE,
    caption_entities: Optional[List[MessageEntity]] = None,
) -> InputMedia:
    if message.content_type == "photo":
        cls = InputMediaPhoto
        media = message.photo[0].file_id
    elif message.content_type == "video":
        cls = InputMediaVideo
        media = message.video.file_id
    elif message.content_type == "audio":
        cls = InputMediaAudio
        media = message.audio.file_id
    elif message.content_type == "document":
        cls = InputMediaDocument
        media = message.document.file_id
    else:
        raise ValueError(f"Unsupported media type {message.content_type}")
    return cls(
        media=media,
        caption=caption or message.caption,
        parse_mode=parse_mode,
        caption_entities=caption_entities or message.caption_entities,
    )


class BaseAlbumMessage(Message, frozen=False):
    _messages: List[Message]

    @classmethod
    def new(cls, messages: List[Message], data: dict[str, Any]) -> "BaseAlbumMessage":
        bot = cast(Bot, data["bot"])
        self = cls.model_validate(messages[0], from_attributes=True).as_(bot)
        self._messages = messages
        setattr(self, messages[0].content_type, None)
        return self

    @property
    def messages(self) -> List[Message]:
        return self._messages

    @property
    def content_type(self) -> str:
        return "media_group"

    def as_input_media(
        self,
        caption: Optional[Union[str, List[str]]] = UNSET,
        parse_mode: Optional[str] = UNSET_PARSE_MODE,
        caption_entities: Optional[
            Union[List[MessageEntity], List[List[MessageEntity]]]
        ] = UNSET,
    ) -> List[InputMedia]:
        if caption is UNSET:
            caption = [None]
        elif isinstance(caption, str):
            caption = [caption]
        if caption_entities is UNSET:
            caption_entities = [None]
        elif isinstance(caption_entities[0], MessageEntity):
            caption_entities = [caption_entities]
        parse_mode = [parse_mode]
        return [
            to_input_media(*args)
            for args in zip_longest(
                self._messages, caption, parse_mode, caption_entities, fillvalue=None
            )
        ]

    @property
    def message_ids(self) -> List[int]:
        return [message.message_id for message in self._messages]

    def __iter__(self) -> Iterator[Message]:
        return self._messages.__iter__()

    def __len__(self) -> int:
        return self._messages.__len__()

    async def copy_to(
        self,
        chat_id: Union[int, str],
        *args,
        **kwargs: Any,
    ) -> Any:
        raise NotImplementedError

    async def forward(
        self,
        chat_id: Union[int, str],
        *args,
        **kwargs: Any,
    ) -> Any:
        raise NotImplementedError

    async def delete(
        self,
        *args,
        **kwargs: Any,
    ) -> Any:
        raise NotImplementedError
