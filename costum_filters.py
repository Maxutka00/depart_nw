import json
import os
import time

from pyrogram.enums.message_entity_type import MessageEntityType
from pyrogram import filters, types, Client
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import CallbackQuery, Message

import db


async def link_filter_func(_, client, message: types.Message):
    if not message.text and not message.caption:
        return False
    else:
        text = (message.text or message.caption).lower()
    if not message.entities:
        return False
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return False
    if db.get_links_whitelist_status(message.chat.id) is False:
        return False
    if message.from_user.id in db.get_chat_admins(message.chat.id, int_list=True):
        return False
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status is ChatMemberStatus.OWNER or user.privileges.can_promote_members:
        db.add_admin(message.chat.id, message.from_user.id)
        return False
    good_links = db.get_chat_links_whitelist(message.chat.id, raw_links=True)
    for entity in message.entities:
        if entity.url:
            if entity.url.split('//')[-1] not in good_links:
                return True
        elif entity.type == MessageEntityType.URL:
            link_in_text = text[entity.offset:entity.length + entity.offset]
            if link_in_text.split('//')[-1] not in good_links:
                return True
        elif entity.type == MessageEntityType.MENTION:
            pass
    return False


link_filter = filters.create(link_filter_func)


async def words_blacklist(_, client, message: types.Message):
    if not message.text and not message.caption:
        return False
    else:
        text = message.text or message.caption
        text = text.lower()
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return False
    if message.from_user.id in db.get_chat_admins(message.chat.id, int_list=True):
        return False
    chat_user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if chat_user.status is ChatMemberStatus.OWNER or (chat_user.privileges and chat_user.privileges.can_promote_members):
        db.add_admin(message.chat.id, message.from_user.id)
        return False
    blacklist = db.get_chat_blacklist(message.chat.id)
    if not blacklist:
        return False
    for word in blacklist:
        if word.lower() in text:
            return True
    return False


words_blacklist_filter = filters.create(words_blacklist)


async def chat_admin(_, client: Client, message: types.Message):
    if isinstance(message, CallbackQuery):
        chat = message.message.chat.id
    elif isinstance(message, Message):
        chat = message.chat.id
    else:
        raise ValueError(f"This filter doesn't work with {type(message)}")
    if message.from_user.id in db.get_chat_admins(chat, int_list=True):
        return True
    user = await client.get_chat_member(chat, message.from_user.id)
    if user.status is ChatMemberStatus.OWNER or (user.privileges and user.privileges.can_promote_members):
        db.add_admin(chat, message.from_user.id)
        return True
    else:
        return False


chat_admin_filter = filters.create(chat_admin)


async def work(_, client: Client, message: Message):
    with open(os.path.join("data", "settings.json"), "r") as f:
        data = json.load(f)
    status = data["work"]
    if status is False:
        return True
    else:
        return False

work_filter = filters.create(work)