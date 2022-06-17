import json
import os
import time

from pyrogram import Client, filters
from pyrogram.types import Message

import config
from func import auto_delete
from func import logger


@Client.on_message(filters.command("repair") & filters.user([1398764450]))
async def change_work(app: Client, message: Message):
    with open(os.path.join("data", "settings.json"), "r") as f:
        data = json.load(f)
    data["work"] = data["work"] is False
    with open(os.path.join("data", "settings.json"), "w") as f:
        json.dump(data, f)
    logger.loggers(message, text="used !repair")
    await message.reply(
        f"Успешно изменён режим: {'бот работает нормально' if data['work'] else 'бот на тех обслуживании'}")
    try:
        if data["work"] is False:
            await app.send_message(config.chat_dp_id,
                               "Просимо вибачення бот тимчасово відключено\n\nЗ однієї або кількох причин:\n— Вийшла з ладу одна з функцій\n- профілактичні виправлення текстів\n- Зміна даних та конфігурації або коду.")
    except Exception as e:
        print(e)


@Client.on_message(filters.command("ping"))
async def ping(app: Client, message: Message):
    logger.loggers(message, text="used !ping")
    a = time.time()
    mes = await message.reply("Pong!")
    b = time.time()
    with open(os.path.join("data", "settings.json"), "r") as f:
        data = json.load(f)
    await mes.edit(
        f"<b>Ping:</b> {round(b - a, 3)}sec.\nСтатус: {'бот работает нормально' if data['work'] else 'бот на тех обслуживании'}")
    await auto_delete.delete_command([mes, message])
    return
