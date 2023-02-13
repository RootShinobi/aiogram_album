from asyncio import run

from aiogram import Bot, Dispatcher, F
from pyrogram import Client

from album_extend import AlbumMessage, AlbumMiddleware

BOT_TOKEN = ""
API_ID = 0
API_HASH = ""

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
dp.message.outer_middleware.register(AlbumMiddleware())
client = Client("my_bot", bot_token=BOT_TOKEN, api_hash=API_HASH, api_id=API_ID)


@dp.message(F.media_group_id)
async def media_handler(message: AlbumMessage):
    await message.reply(
        f"album\n"
        f"size: {len(message)}\n"
        f"content types: {[m.content_type for m in message]}"
    )


async def main():
    await client.start()
    await dp.start_polling(bot, client=client)


run(main())
