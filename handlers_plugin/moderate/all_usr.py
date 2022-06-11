from pyrogram.enums import ChatType
from pyrogram.types import Message
from pyrogram import Client, enums

import costum_filters
import db
from pyrogram import filters


@Client.on_message(costum_filters.work_filter)
async def work(app: Client, message: Message):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await message.reply("Просимо вибачення бот тимчасово відключено\n\nЗ однієї або кількох причин:\n— Вийшла з ладу одна з функцій\n- профілактичні виправлення текстів\n- Зміна даних та конфігурації або коду.")


@Client.on_message(filters.private, group=5)
async def all_usr(app, message: Message):
    db.add_user(message.from_user.id)


@Client.on_message(filters.group, group=5)
async def group_adder(app, message: Message):
    if db.check_chat(message.chat.id) is None:
        administrators = []
        async for m in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            administrators.append(m.user.id)
        db.add_chat(message.chat.id, administrators)
