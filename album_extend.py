from itertools import zip_longest
from typing import Callable, Dict, Any, Awaitable, List, Union, Optional, Iterator

from cachetools import TTLCache

from aiogram import BaseMiddleware
from aiogram.types import (
    Message as AMessage,
    InputMedia,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    PhotoSize,
    Video,
    Document,
    Audio,
    Voice,
    VideoNote,
    UNSET,
    MessageEntity
)

from pyrogram import Client
from pyrogram.types import Message as PMessage


def to_message(message: PMessage) -> AMessage:
    content_type = str(message.media.value)
    message.chat.type = str(message.chat.type.value)

    thumb = getattr(message, content_type).thumbs
    if thumb:
        thumb = thumb[0]
    setattr(message, "thumb", thumb)

    setattr(message, "message_id", message.id)
    setattr(message.chat.photo, "small_file_unique_id", message.chat.photo.small_photo_unique_id)
    setattr(message.chat.photo, "big_file_unique_id", message.chat.photo.big_photo_unique_id)
    if message.forward_date:
        message.forward_date = int(message.forward_date.timestamp())

    if message.photo:
        message.photo = [PhotoSize.from_orm(message.photo)]
    elif message.video:
        message.video = Video.from_orm(message.video)
    elif message.document:
        message.document = Document.from_orm(message.document)
    elif message.audio:
        message.audio = Audio.from_orm(message.audio)
    elif message.video_note:
        message.video_note = VideoNote.from_orm(message.video_note)
    elif message.voice:
        message.voice = Voice.from_orm(message.voice)
    else:
        raise ValueError(f"Unsupported media type {content_type}")

    obj = AMessage.from_orm(message)
    return obj


def to_input_media(
        message: AMessage,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = UNSET,
        caption_entities: Optional[List[MessageEntity]] = None
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
        caption_entities=caption_entities or message.caption_entities
    )


class AlbumMessage(AMessage):
    _client: Client
    _messages: List[AMessage]

    class Config:
        allow_mutation = True

    @property
    def messages(self):
        return self._messages

    @property
    def content_type(self):
        return "media_group"

    async def forward(
            self,
            chat_id: Union[int, str],
            message_thread_id: Optional[int] = None,
            disable_notification: Optional[bool] = None,
            protect_content: Optional[bool] = None,
            **kwargs: Any,
    ) -> Union[PMessage, List[PMessage]]:
        return await self._client.forward_messages(
            chat_id=chat_id,
            from_chat_id=self.chat.id,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_ids=self.message_ids
        )

    async def delete(self) -> int:
        return await self._client.delete_messages(
            chat_id=self.chat.id,
            message_ids=self.message_ids
        )

    @classmethod
    async def from_message(cls, client: Client, message: AMessage) -> "AlbumMessage":
        self = cls.parse_obj(message)

        self._client = client
        self._messages = [to_message(m) for m in await client.get_media_group(
            message.chat.id, message.message_id
        )]
        setattr(self, message.content_type, None)

        return self

    def as_input_media(
            self,
            caption: Optional[Union[str, List[str]]] = UNSET,
            parse_mode: Optional[str] = UNSET,
            caption_entities: Optional[Union[List[MessageEntity], List[List[MessageEntity]]]] = UNSET

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
                self._messages,
                caption,
                parse_mode,
                caption_entities,
                fillvalue=None
            )
        ]

    @property
    def message_ids(self) -> List[int]:
        return [message.message_id for message in self._messages]

    def __iter__(self) -> Iterator[AMessage]:
        return self._messages.__iter__()

    def __len__(self) -> int:
        return self._messages.__len__()


class AlbumMiddleware(BaseMiddleware):
    cache = TTLCache(maxsize=10, ttl=10)

    async def __call__(
            self,
            handler: Callable[[AMessage, Dict[str, Any]], Awaitable[Any]],
            event: AMessage,
            data: Dict[str, Any]
    ) -> Any:
        if event.media_group_id:
            if event.media_group_id in self.cache:
                return
            self.cache[event.media_group_id] = True
            event = await AlbumMessage.from_message(data['client'], event)
        return await handler(event, data)
