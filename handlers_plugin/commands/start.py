from loguru import logger
from pyrogram import filters, enums
from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.types import Message

import db
from func import auto_delete


@Client.on_message(filters.command("start"))
async def start(app, message: Message):
    logger.info(
        f'user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | used !start is private chat')
    mes = await app.send_message(chat_id=message.chat.id, text='''Щоб дізнатись розклад Автобусного маршруту напишіть:
Автобус [номер Автобуса]
— Автобус 151а
— Автобус 77
— Автобус 1

Щоб дізнатись розклад Тролейбусного маршруту напишіть:
Тролейбус [номер Тролейбуса]
— Тролейбус 1
— Тролейбус 5
— Тролейбус б

Щоб дізнатись розклад Трамвайного маршруту напишіть:
Трамвай [номер Трамвая]
— Трамвай 1
— Трамвай 9
— Трамвай 19

Також э команди для адміністрації груп, напишить /help
''')
    if message.chat.type is ChatType.PRIVATE:
        db.add_user(message.from_user.id)
    elif message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
        if db.check_chat(message.chat.id):
            administrators = []
            async for m in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                administrators.append(m.user.id)
            db.add_chat(message.chat.id, administrators)
    await auto_delete.delete_command([message, mes])
