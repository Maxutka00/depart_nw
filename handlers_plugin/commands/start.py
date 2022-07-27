from loguru import logger
from pyrogram import filters, enums
from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.types import Message, CallbackQuery

import config
import db
from func import auto_delete
from func import logger
from keyboards import inline


@Client.on_message(filters.command("start"))
async def start(app, message: Message):
    logger.loggers(message, text="used !start")
    mes_text = '''Щоб дізнатись розклад Автобусного/трамвайного/троллейбусного маршруту напишіть:
Автобус [номер Автобуса/Трамвайя/Троллейбуса]
— Автобус 146б
— Трамвай 1
— Тролейбус 1

В Разроботке:
— Рассписание пригородных маршрутов
— рассписание метро
— рассписание электричек.
— рассписание междугородних поездов также международный

Для того чтоб узнать все команды для администрации группы, напишите /help

По всем вопросам или предложениям по роботе бота а также сотрудничества можете писать сюда. https://t.me/Dnipro_transport_support
Очень ждём.'''
    ref = None
    if message.chat.type in (ChatType.PRIVATE, ChatType.BOT):
        if len(message.command) > 1 and message.command[1].isdigit() and int(message.command[1]) in config.ref_links:
            ref = int(message.command[1])
        else:
            ref = None
        db.add_user(message.from_user.id, ref)
        if db.get_user_mail(message.from_user.id) is False:
            mes_text += "\n\nДля того чтоб подписаться на рассылку Новостей департамента транспорта воспользуйтесь командой /mail"
    elif message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
        if db.check_chat(message.chat.id):
            administrators = []
            async for m in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                administrators.append(m.user.id)
            db.add_chat(message.chat.id, administrators)
    mes_text += "\n\nКнопкой ниже вы можете получить реквизиты для поддержки бота."
    mes = await app.send_message(message.chat.id, mes_text, reply_markup=inline.donate_kb())
    if ref:
        await message.reply(config.ref_links.get(ref))
    await auto_delete.delete_command([message, mes])


@Client.on_callback_query(filters.regex("donate"))
async def donate(app: Client, callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup()
    await callback_query.message.reply("Ви можете надати гроші для сплати за сервер для роботи бота та підтримки адміністрації бота\n\n🔗Посилання на Банку\nhttps://send.monobank.ua/jar/6E85edaBFL\n\n💳Номер карти Банки\n<code>5375 4112 0229 7482</code>")
