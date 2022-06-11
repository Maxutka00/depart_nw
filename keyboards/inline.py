from typing import Literal, Optional
import os
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from func.translit import translit


def electric_transport_kb(transport: Literal["trol", "tram"], num: str) -> Optional[InlineKeyboardMarkup]:
    files = list(filter(lambda x: x.startswith(f"{num}{transport}"), os.listdir(os.path.join("parsing", "photos"))))
    if len(files) == 1:
        return None
    kb = []
    for file in files:
        file = file.replace(".png", "").replace("'", '"').replace("bsl", "\\").replace("sl", "/")
        name = file.split('_')
        name = f"{name[1]} {('(до ' + name[2] + ')') if name[2] != '' else ''}"
        file = translit(file)
        button = InlineKeyboardButton(name, callback_data=file)
        kb.append([button])
    return InlineKeyboardMarkup(kb) if kb else None


def del_mute_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton("Снять мут", callback_data=f"unmute_{user_id}")]]
    return InlineKeyboardMarkup(kb)
