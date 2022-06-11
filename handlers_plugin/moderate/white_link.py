from datetime import timedelta, datetime

from pyrogram import Client
from pyrogram.errors import UserAdminInvalid, ChannelInvalid, ChatAdminRequired
from pyrogram.types import ChatPermissions

import costum_filters


@Client.on_message(costum_filters.link_filter)
async def white_list_link(app, message):
    try:
        await message.delete()
    except Exception as e:
        print(e)
    num_warn = db.add_warn(message.chat.id, message.reply_to_message.from_user.id, "отправлена ссылка")
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
                           f"Вам был выдан варн. Всего их у вас {num_warn}\nПричина: отправлена ссылка\nНаказание: {punishment}",
                           reply_to_message_id=message.reply_to_message_id)
