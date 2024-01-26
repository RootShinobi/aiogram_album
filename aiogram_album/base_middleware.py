from abc import abstractmethod
from typing import Any, Awaitable, Callable, Optional, Dict

from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import Message, TelegramObject, Update

from .album_message import AlbumMessage


class BaseAlbumMiddleware(BaseMiddleware):
    def __init__(self, dispatcher: Optional[Dispatcher] = None) -> None:
        if dispatcher:
            dispatcher.update.outer_middleware.register(self)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        if not event.message or not event.message.media_group_id:
            return await handler(event, data)
        if album_message := await self.handle(
            message=event.message,
            data=data,
        ):
            event = event.model_copy(update={"message": album_message})
            return await handler(event, data)

    @abstractmethod
    async def handle(
        self,
        message: Message,
        data: Dict[str, Any],
    ) -> Optional[AlbumMessage]:
        pass
