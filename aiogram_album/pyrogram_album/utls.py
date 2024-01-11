from aiogram import Bot
from aiogram.types import Message, PhotoSize, Video, Document, Audio, VideoNote, Voice
from pyrogram.types import Message as PyrogramMessage


def to_message(message: PyrogramMessage, bot: Bot) -> Message:
    content_type = str(message.media.value)

    thumb = getattr(message, content_type).thumbs
    if thumb:
        thumb = thumb[0]
    message.thumb = thumb

    message.message_id = message.id
    if message.chat:
        message.chat.type = message.chat.type.value
        if message.chat.photo:
            message.chat.photo.small_file_unique_id = message.chat.photo.small_photo_unique_id
            message.chat.photo.big_file_unique_id = message.chat.photo.big_photo_unique_id

    if message.forward_date:
        message.forward_date = int(message.forward_date.timestamp())

    if message.photo:
        message.photo = [PhotoSize.model_validate(message.photo, from_attributes=True)]
    elif message.video:
        message.video = Video.model_validate(message.video, from_attributes=True)
    elif message.document:
        message.document = Document.model_validate(
            message.document, from_attributes=True
        )
    elif message.audio:
        message.audio = Audio.model_validate(message.audio, from_attributes=True)
    elif message.video_note:
        message.video_note = VideoNote.model_validate(
            message.video_note, from_attributes=True
        )
    elif message.voice:
        message.voice = Voice.model_validate(message.voice, from_attributes=True)
    else:
        raise ValueError(f"Unsupported media type {content_type}")

    # stupid pydantic fix
    message.media_group_id = str(message.media_group_id)

    obj = Message.model_validate(message, from_attributes=True)

    return obj.as_(bot=bot)
