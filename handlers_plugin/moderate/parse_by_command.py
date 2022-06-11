import time

from pyrogram import Client, filters
from pyrogram.types import Message
import threading
import config
from parsing import parse


@Client.on_message(filters.command("parse") & filters.user(config.default_admins))
async def start_parse(app: Client, message: Message):
    await message.delete()
    a = time.time()
    try:
        parse.transport_parse()
    except Exception as e:
        await app.send_message(message.from_user.id, f"Ошибка при парсинге автобусов:\n{e}")
    threading.Thread(target=parse.electric_transport_parse).start()