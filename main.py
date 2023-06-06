from asyncio import run

from aiogram import Bot, Dispatcher, F, Router
from pyrogram import Client

from album_extend import AlbumMessage, AlbumMiddleware

BOT_TOKEN = ""
API_ID = 0
API_HASH = ""

bot = Bot(BOT_TOKEN)
router = Router()
client = Client("my_bot", bot_token=BOT_TOKEN, api_hash=API_HASH, api_id=API_ID)


@router.message(F.media_group_id)
async def media_handler(message: AlbumMessage):
    await message.reply(
        f"album\n"
        f"size: {len(message)}\n"
        f"content types: {[m.content_type for m in message]}"
    )
    await message.copy_to(
        message.chat.id
    )


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    AlbumMiddleware(client=client, router=dp)
    await client.start()
    await dp.start_polling(bot, client=client)


run(main())
