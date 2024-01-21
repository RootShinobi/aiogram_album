from aiogram import Bot
from aiogram.types import Message, PhotoSize, Video, Document, Audio, VideoNote, Voice
from pyrogram.types import Message as PyrogramMessage, Chat


def chat_fix(chat: Chat):
    chat.type = chat.type.value
    if chat.photo:
        chat.photo.small_file_unique_id = chat.photo.small_photo_unique_id
        chat.photo.big_file_unique_id = chat.photo.big_photo_unique_id


def to_message(message: PyrogramMessage, bot: Bot) -> Message:
    content_type = str(message.media.value)

    thumb = getattr(message, content_type).thumbs
    if thumb:
        thumb = thumb[0]
    message.thumb = thumb

    message.message_id = message.id

    if message.chat:
        chat_fix(message.chat)

    if message.forward_from_chat:
        chat_fix(message.forward_from_chat)

    if message.sender_chat:
        chat_fix(message.sender_chat)

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

    message.media_group_id = str(message.media_group_id)

    obj = Message.model_validate(message, from_attributes=True)

    return obj.as_(bot=bot)
