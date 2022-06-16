import asyncio
import re
from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.errors import UserAdminInvalid, ChatAdminRequired, ChannelInvalid
from pyrogram.types import Message, ChatPermissions, CallbackQuery

import costum_filters
import db
from func import auto_delete
from keyboards.inline import del_mute_kb


async def message_deleter(message, time: int = 180):
    await asyncio.sleep(time)
    try:
        await message.delete()
    except Exception as e:
        print(e)


@Client.on_message(filters.command("report", prefixes=["/", "!"]) & filters.group & filters.reply)
async def report(app: Client, message: Message):
    await message.delete()
    report_chat = db.get_report_chat(message.chat.id)
    if report_chat == 0:
        chats = db.get_chat_admins(message.chat.id)
    else:
        chats = [report_chat]
    for chat in chats:
        try:
            await app.send_message(chat,
                                   f"Вызов администрации\nКоманду вызвал: {message.from_user.mention} на {message.reply_to_message.from_user.mention}\n\nСсылка на сообщение:\n{message.reply_to_message.link}")
        except Exception as e:
            print(e)
    mes = await message.reply("Ваше сообщение было доставлено администрации")
    messages = [mes, message]
    await auto_delete.delete_command(messages)


@Client.on_message(filters.command(["warn", "w"], prefixes=["/",
                                                            "!"]) & filters.group & filters.reply & costum_filters.chat_admin_filter)
async def warn(app: Client, message: Message):
    if message.sender_chat:
        return await message.reply("Невозможно выдать варн, человек пишет не от своего имени")
    mes1 = None
    if len(message.command) < 2:
        mes = await message.reply("Вы не указали аргументы")
        await auto_delete.delete_command([mes, message], 10)
        return
    arg = message.command[1]
    if arg == 'del' and len(message.command) > 2:
        if not message.command[2].isdigit():
            mes = await message.reply("Неверный номер варна")
            await auto_delete.delete_command([mes, message], 10)
            return
        status = db.del_warn(message.chat.id, message.reply_to_message.from_user.id, int(message.command[2]))
        if status:
            mes = await message.reply("Варн успешно удалён",
                                      reply_markup=del_mute_kb(message.reply_to_message.from_user.id))
        else:
            mes = await message.reply("Нoмер варна указан не верно")
    else:
        reason = message.text.split(maxsplit=1)[1]
        num_warn = db.add_warn(message.chat.id, message.reply_to_message.from_user.id, reason)
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
            mes1 = await message.reply('Варн добавлен, но у бота нет прав на мут')
            punishment = "нет"
        except ChannelInvalid:
            mes1 = await message.reply('Варн добавлен, но мут работает только в супергруппах')
            punishment = "нет"
        else:
            punishment = f"мут {hours}ч."
        mes = await app.send_message(message.chat.id,
                                     f"Вам был выдан варн. Всего их у вас {num_warn}\nПричина: {reason}\nНаказание: {punishment}",
                                     reply_to_message_id=message.reply_to_message_id)
    await auto_delete.delete_command([mes, message, mes1])


@Client.on_message(
    filters.command(["info"], prefixes=["/", "!"]) & filters.group & filters.reply & costum_filters.chat_admin_filter)
async def info(app: Client, message: Message):
    warns = db.get_warns(message.chat.id, message.reply_to_message.from_user.id)
    text = f"Юзер: {message.reply_to_message.from_user.mention}\nID: <code>{message.reply_to_message.from_user.id}</code>"
    text_warns = []
    if not warns:
        text_warns = ["Варнов нет"]
    for num, warn in enumerate(warns, start=1):
        text_warns.append(f"{num}. {warn}")
    text_warns = '\n'.join(text_warns)
    mes = await message.reply(f"{text}\n\nВарны:\n{text_warns}")
    await auto_delete.delete_command([mes, message])


@Client.on_callback_query(filters.regex(r"unmute_\d+", re.I) & costum_filters.chat_admin_filter)
async def unmute(app: Client, callback_query: CallbackQuery):
    user = int(callback_query.data.split('_')[-1])
    try:
        await app.restrict_chat_member(callback_query.message.chat.id, user, callback_query.message.chat.permissions)
    except (UserAdminInvalid, ChatAdminRequired):
        await callback_query.message.edit(f"{callback_query.message.text}\n<i>У бота нет прав</i>")
        return
    await callback_query.message.edit(f"{callback_query.message.text}\nМут снят")
