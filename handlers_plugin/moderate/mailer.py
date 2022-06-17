import asyncio
import time

from pyrogram import Client, filters
from pyrogram.types import Message

import config
import db
from func import logger


@Client.on_message(filters.command("mailer") & filters.reply & filters.user([594165498, 666445915]))
async def mailer(app: Client, message: Message):
    logger.loggers(message, text="used !mailer")
    users = db.get_all_users()
    a = time.time()
    fail = 0
    correct = 0
    await message.reply("Рассылка началась\nВсего пользователей: {}".format(len(users)))
    for user in users:
        try:
            await app.copy_message(user, message.chat.id, message.reply_to_message_id)
        except Exception as e:
            fail += 1
            #print(e)
        else:
            correct += 1
        await asyncio.sleep(.05)
    b = time.time()
    await message.reply("Отправлено всем пользователям бота в течение " + str(b - a) + " секунд\nВсего юзеров: " + str(len(users)) + "\nУспешно: " + str(correct) + "\nНеудачно: " + str(fail))
