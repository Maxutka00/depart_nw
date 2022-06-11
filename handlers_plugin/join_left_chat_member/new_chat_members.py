from loguru import logger
from pyrogram import Client
from pyrogram import filters

import config


# Новенькие на канале


@Client.on_message(filters.chat(config.chat_dp_id) & filters.new_chat_members)
async def new_chat_members(app, message):
    try:
        for i in message.new_chat_members:
            logger.info(
                f'user_id = {i.id} | first_name = {i.first_name} | last_name = {i.last_name} | joined the chat')
        await app.delete_messages(message.chat.id, message.id)
    except Exception as e:
        print(e)


