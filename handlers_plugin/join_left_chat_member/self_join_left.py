from pyrogram import Client
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus
from pyrogram.types import ChatMemberUpdated

import db


@Client.on_chat_member_updated()
async def add_bot_to_chat(app, update: ChatMemberUpdated):
    if update.old_chat_member:
        if update.old_chat_member.user.is_self:
            db.del_chat(update.chat.id)
    elif update.new_chat_member:
        if update.new_chat_member.user.is_self:
            admins = [(i.user.id if i.status == ChatMemberStatus.OWNER else ...) async for i in app.get_chat_members(update.chat.id, filter=ChatMembersFilter.ADMINISTRATORS)]
            db.add_chat(update.chat.id, admins)

