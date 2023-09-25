from asyncio import run
from typing import Annotated

import uvicorn
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Update
from fastapi import FastAPI, Header
from pyrogram import Client

from album_extend import AlbumMiddleware, AlbumMessage

BOT_TOKEN = ""
API_ID = 0
API_HASH = ""
WEBHOOK_PATH = "/bot"
URL = "https://localhost"
WEBHOOK_URL = f"{URL}{WEBHOOK_PATH}"

SECRET = "secret"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
router = Router()
client = Client(
    "my_bot", bot_token=BOT_TOKEN, api_hash=API_HASH, api_id=API_ID, no_updates=True
)

web = FastAPI()


@router.message(F.media_group_id)
async def media_handler(message: AlbumMessage):
    await message.reply(
        f"album\n"
        f"size: {len(message)}\n"
        f"content types: {[m.content_type for m in message]}"
    )
    await message.copy_to(message.chat.id)


@web.on_event("startup")
async def on_startup() -> None:
    webhook_info = await bot.get_webhook_info()
    if webhook_info != WEBHOOK_URL:
        await bot.set_webhook(
            drop_pending_updates=True, url=WEBHOOK_URL, secret_token=SECRET
        )


@web.on_event("shutdown")
async def on_shutdown() -> None:
    await dp.storage.close()
    await bot.delete_webhook(drop_pending_updates=True)


@web.post(WEBHOOK_PATH)
async def bot_webhook(
    update: Update,
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
) -> None:
    if x_telegram_bot_api_secret_token != SECRET:
        return None
    await dp.feed_webhook_update(bot, update)


async def main():
    dp.include_router(router)
    dp.startup.register(on_startup)

    AlbumMiddleware(client=client, router=dp)

    dp["client"] = client

    config = uvicorn.Config("__main__:web", port=8080, log_level="info")
    server = uvicorn.Server(config)

    await client.start()
    await server.serve()


run(main())
