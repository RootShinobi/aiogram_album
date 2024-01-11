# aiogram album

## Base handler
```python
from aiogram_album import AlbumMessage

@router.message(F.media_group_id)
async def media_handler(message: AlbumMessage):
    await message.reply(
        f"album\n"
        f"size: {len(message)}\n"
        f"content types: {[m.content_type.value for m in message]}"
    )
```

## PyrogramAlbumMiddleware
_Install_
```bash
pip install aiogram_album Pyrogram cachetools TgCrypto
```
_Usage_

> [!CAUTION]
> Obtain the API key by following Telegram’s instructions and rules at https://core.telegram.org/api/obtaining_api_id

```python
from aiogram_album.pyrogram_album.middleware import PyrogramAlbumMiddleware



await PyrogramAlbumMiddleware.from_app_data(
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    router=dp,
)
```

## TTLCacheAlbumMiddleware
_Install_
```bash
pip install aiogram_album cachetools
```
_Usage_
```python
from aiogram_album.ttl_cache_middleware import TTLCacheAlbumMiddleware


TTLCacheAlbumMiddleware(router=dp)
```

## CountCheckAlbumMiddleware
_Install_
```bash
pip install aiogram_album
```
_Usage_
```python
from aiogram_album.count_check_middleware import CountCheckAlbumMiddleware


CountCheckAlbumMiddleware(router=dp)
```

## WithoutCountCheckAlbumMiddleware
_Install_
```bash
pip install aiogram_album
```
_Usage_
```python
from aiogram_album.no_check_count_middleware import WithoutCountCheckAlbumMiddleware


WithoutCountCheckAlbumMiddleware(router=dp)
```
