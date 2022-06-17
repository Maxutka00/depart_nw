from typing import Literal, Optional
import os
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from func.translit import translit


def electric_transport_kb(transport: Literal["trol", "tram"], num: str) -> Optional[InlineKeyboardMarkup]:
    files = list(filter(lambda x: x.startswith(f"{num}{transport}"), os.listdir(os.path.join("parsing", "photos"))))
    if len(files) == 1:
        return None
    files.sort(key=lambda x: os.path.getmtime(os.path.join("parsing", "photos", x)))
    kb = []
    for file in files:
        file = file.replace(".png", "").replace("'", '"').replace("бслеш", "\\").replace("слеш", "/")
        name = file.split('_')
        name = f"{name[1]} {('(до ' + name[2] + ')') if name[2] != '' else ''}"
        file = translit(file)
        button = InlineKeyboardButton(name, callback_data=file)
        kb.append([button])
    return InlineKeyboardMarkup(kb) if kb else None


def del_mute_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton("Снять мут", callback_data=f"unmute_{user_id}")]]
    return InlineKeyboardMarkup(kb)


def donate_kb() -> Optional[InlineKeyboardMarkup]:
    if config.donate_link == "":
        return None
    kb = [[InlineKeyboardButton("Пожервовать", url=config.donate_link)]]
    return InlineKeyboardMarkup(kb)