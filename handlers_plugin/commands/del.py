from loguru import logger
from pyrogram import filters
from pyrogram import Client

import config
from costum_filters import chat_admin_filter


@Client.on_message(filters.command("del", prefixes=config.prefix) & chat_admin_filter)
async def dels(app, message):
	logger.info(f'user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | used !del')
	await app.delete_messages(message.chat.id, message.id)
	if message.reply_to_message:
		await app.delete_messages(message.chat.id, message.reply_to_message.id)
	else:
		await message.reply("Вы не ответили на сообщение")