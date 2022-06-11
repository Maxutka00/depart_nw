from loguru import logger
from pyrogram import Client
from pyrogram import filters

import config


# Уебавшие из канала


@Client.on_message(filters.chat(config.chat_dp_id) & filters.left_chat_member)
async def left_chat_member(app, message):
    try:
        logger.info(
            f'user_id = {message.left_chat_member.id} | first_name = {message.left_chat_member.first_name} | last_name = {message.left_chat_member.last_name} | Left the chat')
        await app.delete_messages(message.chat.id, message.id)
    except Exception as e:
        print(e)



