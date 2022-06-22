from loguru import logger
from pyrogram import Client
from pyrogram import filters
from func import logger
import config


# Новенькие на канале


@Client.on_message(filters.chat(config.chat_dp_id) & filters.new_chat_members)
async def new_chat_members(app, message):
    try:
        for i in message.new_chat_members:
            logger.loggers(i, text="joined the chat")
        await message.delete()
    except Exception as e:
        print(e)


