import os

from pyrogram import filters
from pyrogram import Client
import config
import db
from func import logger


@Client.on_message(filters.command("send_log", prefixes=["/", config.prefix]) & filters.user(config.admins))
async def send_log(app, message):
    logger.loggers(message, text="send logs")
    await app.send_document(message.chat.id, os.path.join("logs", "logger.log"))


@Client.on_message(filters.command("ref", prefixes=["/", config.prefix]) & filters.user(config.admins))
async def send_ref(app: Client, message):
    bot = await app.get_me()
    text = ""
    for i in config.ref_links:
        text += f"\n\nhttps://t.me/{bot.username}/?start={i}\n{config.ref_links.get(i)}\nКол-во: {len(db.get_ref_users(i))}"

    await message.reply(text)
