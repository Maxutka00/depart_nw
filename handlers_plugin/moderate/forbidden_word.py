from datetime import datetime, timedelta

from loguru import logger
from pyrogram import filters
from pyrogram import Client
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid, ChannelInvalid
from pyrogram.types import ChatPermissions

import db
from costum_filters import words_blacklist_filter


@Client.on_message(words_blacklist_filter & ~filters.forwarded)
async def text_mat(app, message):
    try:
        logger.info(
            f'user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | used a forbidden word')
        await app.delete_messages(message.chat.id, message.id)
    except Exception as e:
        print(e)
    num_warn = db.add_warn(message.chat.id, message.reply_to_message.from_user.id, "использовано запрещённое слово")
    if num_warn == 1:
        hours = 3
    elif num_warn == 2:
        hours = 24
    elif num_warn > 2:
        hours = 24 * 7
    else:
        hours = 24 * 7

    try:
        await app.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, ChatPermissions(),
                                       datetime.now() + timedelta(hours=hours))
    except (UserAdminInvalid, ChatAdminRequired):
        await message.reply('Варн добавлен, но у бота нет прав на мут')
        punishment = "нет"
    except ChannelInvalid:
        await message.reply('Варн добавлен, но мут работает только в супергруппах')
        punishment = "нет"
    else:
        punishment = f"мут {hours}ч."
    await app.send_message(message.chat.id,
                       f"Вам был выдан варн. Всего их у вас {num_warn}\nПричина: использовано запрещённое слово\nНаказание: {punishment}",
                       reply_to_message_id=message.reply_to_message_id)
