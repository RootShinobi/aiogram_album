from asyncio import run, sleep

from aiogram import Bot, Dispatcher, F, Router
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from pyrogram import Client

from album_extend import AlbumMessage, AlbumMiddleware

BOT_TOKEN = ""
API_ID = 0
API_HASH = ""
WEBHOOK_PATH = "/bot"
URL = "https://localhost"
WEBHOOK_URL = f"{URL}{WEBHOOK_PATH}"

SECRET = "secret"

bot = Bot(BOT_TOKEN)
router = Router()
client = Client(
    "my_bot", bot_token=BOT_TOKEN, api_hash=API_HASH, api_id=API_ID, no_updates=True
)
app = web.Application()
runner = web.AppRunner(app)


@router.message(F.media_group_id)
async def media_handler(message: AlbumMessage):
    await message.reply(
        f"album\n"
        f"size: {len(message)}\n"
        f"content types: {[m.content_type for m in message]}"
    )
    await message.copy_to(message.chat.id)


async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(
        WEBHOOK_URL,
        secret_token=SECRET,
        drop_pending_updates=True,
    )


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(on_startup)
    AlbumMiddleware(client=client, router=dp)

    dp["client"] = client

    webhook_request_handler = SimpleRequestHandler(
        dispatcher=dp, bot=bot, secret_token=SECRET
    )

    webhook_request_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 8080)
    await site.start()

    print(f"Running on {site.name}")

    await client.start()

    while True:
        await sleep(3600)


run(main())
