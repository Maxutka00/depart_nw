from loguru import logger
from pyrogram import Client
from pyrogram import filters

import config
from func import logger


@Client.on_message(filters.chat(config.chat_dp_id) & filters.left_chat_member)
async def left_chat_member(app, message):
    try:
        logger.loggers(message, text="left is chat")
        await message.delete()
    except Exception as e:
        print(e)



