import asyncio
import time

from pyrogram import Client, filters
from pyrogram.types import Message

import config
import db
from func import logger, auto_delete


@Client.on_message(filters.command("mailer") & filters.reply & filters.user([1398764450, 29764093, 666445915]))
async def mailer(app: Client, message: Message):
    logger.loggers(message, text="used !mailer")
    if len(message.command) < 2 or message.command[1] not in ("1", "0", "2") or (len(message.command) >= 3 and message.command[2] not in ("1", "0", "2")):
        await message.reply("Укажите аргументы\n/mailer [2 - без подписки, 1 - c подпиской, 0 - всем] [0 - оффициал канал, 1 - Оффициал Предствитель, 2 - Пустуо]")
        return

    users = db.get_all_users((int(message.command[1])))
    a = time.time()
    fail = 0
    correct = 0
    await message.reply("Рассылка началась\nВсего пользователей: {}".format(len(users)))
    for user in users:
        try:
            await app.copy_message(user, message.chat.id, message.reply_to_message_id)
        except Exception as e:
            fail += 1
            # print(e)
        else:
            correct += 1
        await asyncio.sleep(.05)
    b = time.time()
    await message.reply(
        "Отправлено пользователям бота в течение " + str(round(b - a, 2)) + " секунд\nВсего юзеров: " + str(
            len(users)) + "\nУспешно: " + str(correct) + "\nНеудачно: " + str(fail))


@Client.on_message(filters.command("mail"))
async def sub_to_mail(app: Client, message: Message):
    logger.loggers(message, text="used !mail")
    data = db.get_user_mail(message.from_user.id)
    db.set_user_mail(message.from_user.id, data is False)
    if data:
        mes = await message.reply(
            "Нам дуже шкода що ви відписалися від розсилки, якщо хочете підписатся відправте команду /mail ще раз")
    else:
        mes = await message.reply(
            "Cпасибі що підписалися на розсилку, якщо хочете відписатся відправте команду /mail ще раз")

    await auto_delete.delete_command([message, mes])
