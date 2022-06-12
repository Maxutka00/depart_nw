import os
import sqlite3
from pprint import pprint
from typing import List, Union, Tuple, Optional

import config


def prepare_db():
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        cursor.executescript("""CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY,
        admins TEXT,/*admin1 admin2 admin3*/
        links_whitelist TEXT,/*link1;link2;link3*/
        links_whitelist_status INTEGER, /*1-вкл, 0-выкл*/
        words_blacklist TEXT,/*word1;word2;word3*/
        night_mode_on TEXT,/*23 00*/
        night_mode_off TEXT,/*5 00*/
        night_mode_status INTEGER, /*1-вкл, 0-выкл*/
        report_chat INTEGER,/*если 0 то отправляется всем админам*/
        auto_delete_commands INTEGER,/*время автоудаления команд в сек, 0 = не удалять*/
        auto_delete_timetables INTEGER/*время автоудаления расписания в сек, 0 = не удалять*/
        );/*Это просто были примеры*/
        CREATE TABLE IF NOT EXISTS warns(
        chat_id INTEGER,
        user_id INTEGER,
        warns TEXT); /*warn1;;warn2;;warn3*/
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS buses(
        num_route TEXT, /* номер маршрута, если есть буква, то в нижнем регистре*/
        way_place TEXT, /*шлях прямування, также как и в таблице*/
        way_time TEXT, /*время первого и последнего рейса, также как и в таблице, но без доп инфы*/
        different_time_data TEXT, /*если есть обозначения дня недели(выходной, рабочие и тд), иначе None*/
        intervals TEXT, /*если 3 последних калони разделены, пример данных 20;15;20, иначе None*/
        interval_data TEXT, /*текст который записан в трёх последних колонках, при условии что они объеденины, иначе None*/
        work INTEGER /*1-работает, 2-не работает*/
        );""")
        chat = cursor.execute("SELECT * FROM chats WHERE id=?", (config.chat_dp_id,)).fetchone()
        if chat is not None:
            return
        args = (config.chat_dp_id, ' '.join(list(map(str, config.default_admins))), ';'.join(config.links_whitelist), 1,
                ';'.join(config.words_blacklist), '23 00', '5 00', 1, config.report_chat_dp, 120, 600)
        cursor.execute("""INSERT INTO chats VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", args)
        conn.commit()


def add_transport(transport_list: Union[List[Union[Tuple, List]], Tuple[Union[Tuple, List]]], del_all=True):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        if del_all:
            cursor.execute("""DELETE FROM buses""")
        for data in transport_list:
            cursor.execute("""INSERT INTO buses VALUES(?, ?, ?, ?, ?, ?, ?)""", data)
        conn.commit()


def get_transport(num_route: str) -> Optional[List]:
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        data = cursor.execute("""SELECT * FROM buses WHERE num_route = ?""",
                              (num_route,)).fetchall()
        return data


def add_user(user_id: int, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        user = cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if user is None:
            cursor.execute("INSERT INTO users Values (?)", (user_id,))
            conn.commit()
            return True
        else:
            return False


def add_chat(chat_id: int, admins: List, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        chat = cursor.execute("SELECT * FROM chats WHERE id=?", (chat_id,)).fetchone()
        if chat is None:
            if chat_id != config.chat_dp_id:
                args = (chat_id, ' '.join(list(map(str, admins))), '', 0,
                        '', '23 00', '5 00', 0, 0, 0, 0)
            else:
                args = (
                    config.chat_dp_id, ' '.join(list(map(str, config.default_admins))),
                    ';'.join(config.links_whitelist), 1,
                    ';'.join(config.words_blacklist), '23 00', '5 00', 1, config.report_chat_dp, 120, 600)
            cursor.execute("""INSERT INTO chats VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", args)
            conn.commit()
            return True
        else:
            return False


def del_chat(chat_id: int, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        cursor.execute("""DELETE FROM chats WHERE id = ?""", (chat_id,))
        conn.commit()


def get_all_chats():
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        data = cursor.execute("""SELECT * FROM chats""")
        return data.fetchall()


def check_chat(chat_id: int):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        chat = cursor.execute("SELECT * FROM chats WHERE id=?", (chat_id,)).fetchone()
        return chat


#################################


def add_admin(chat_id: int, admin_id, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        admins = get_chat_admins(chat_id, int_list=False)
        if str(admin_id) in admins:
            return False
        admins.append(str(admin_id))
        cursor.execute("""UPDATE chats SET admins = ? WHERE id = ?""", (' '.join(admins), chat_id))
        conn.commit()
        return True


def get_chat_admins(chat_id: int, int_list: bool = True, ) -> Union[List[str], List[int]]:
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        admins = cursor.execute("SELECT admins FROM chats WHERE id=?", (chat_id,)).fetchone()
        if admins is None:
            add_chat(chat_id, [])
            return []
        admins = admins[0]
        if int_list:
            return list(map(int, admins.split()))
        return admins.split()


def del_admin(chat_id: int, admin_id, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        admins = get_chat_admins(chat_id, int_list=False)
        try:
            index = admins.index(str(admin_id))
        except ValueError:
            return False
        admins.pop(index)
        cursor.execute("""UPDATE chats SET admins = ? WHERE id = ?""", (' '.join(admins), chat_id))
        conn.commit()
        return True


#########################


def get_chat_blacklist(chat_id: int, ) -> List[str]:
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        admins = cursor.execute("SELECT words_blacklist FROM chats WHERE id=?", (chat_id,)).fetchone()[0]
        if admins == '':
            return []
        return admins.split(';')


def add_word_to_blacklist(chat_id: int, word: str, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        words_blacklist = get_chat_blacklist(chat_id)
        word = word.strip()
        if str(word) in words_blacklist:
            return False
        words_blacklist.append(word)
        cursor.execute("""UPDATE chats SET words_blacklist = ? WHERE id = ?""", (';'.join(words_blacklist), chat_id))
        conn.commit()
        return True


def del_word_from_blacklist(chat_id: int, word: str, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        words_blacklist = get_chat_blacklist(chat_id)
        word = word.strip()
        try:
            index = words_blacklist.index(word)
        except ValueError:
            return False
        words_blacklist.pop(index)
        cursor.execute("""UPDATE chats SET words_blacklist = ? WHERE id = ?""", (';'.join(words_blacklist), chat_id))
        conn.commit()
        return True


######################


def get_chat_links_whitelist(chat_id: int, raw_links: bool = False, ) -> List[str]:
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        links_whitelist = cursor.execute("SELECT links_whitelist FROM chats WHERE id=?", (chat_id,)).fetchone()[0]
        if links_whitelist == '':
            return []
        links = links_whitelist.split(';')
        if raw_links:
            links = list(map(lambda x: x.split('//')[-1], links))
        return links


def add_link_to_whitelist(chat_id: int, link: str, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        links_whitelist = get_chat_links_whitelist(chat_id)
        link = link.strip()
        if str(link) in links_whitelist:
            return False
        links_whitelist.append(link)
        cursor.execute("""UPDATE chats SET links_whitelist = ? WHERE id = ?""", (';'.join(links_whitelist), chat_id))
        conn.commit()
        return True


def del_link_from_whitelist(chat_id: int, link: str, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        links_whitelist = get_chat_links_whitelist(chat_id)
        link = link.strip()
        try:
            index = links_whitelist.index(link)
        except ValueError:
            return False
        links_whitelist.pop(index)
        cursor.execute("""UPDATE chats SET links_whitelist = ? WHERE id = ?""", (';'.join(links_whitelist), chat_id))
        conn.commit()
        return True


def get_links_whitelist_status(chat_id: int, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        data = cursor.execute("""SELECT links_whitelist_status FROM chats WHERE id = ?""", (chat_id,))
        return bool(data.fetchone()[0])


def enable_links_whitelist_mode(chat_id: int, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        cursor.execute("""UPDATE chats SET links_whitelist_status = ? WHERE id = ?""", (1, chat_id))
        conn.commit()


def disable_links_whitelist_mode(chat_id: int, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        cursor.execute("""UPDATE chats SET links_whitelist_status = ? WHERE id = ?""", (0, chat_id))
        conn.commit()


######################


def get_night_mode(chat_id: int, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        data = cursor.execute("""SELECT night_mode_on, night_mode_off, night_mode_status FROM chats WHERE id = ?""",
                              (chat_id,)).fetchone()
        return data


def change_night_mode_time(chat_id: int, change: str, set_time: str, ):
    """Argument "change" can be only "start" or "stop\""""
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        if change == 'start':
            cursor.execute("""UPDATE chats SET night_mode_on = ? WHERE id = ?""", (set_time, chat_id))
        elif change == 'stop':
            cursor.execute("""UPDATE chats SET night_mode_off = ? WHERE id = ?""", (set_time, chat_id))
        else:
            return False
        conn.commit()
        return True


def enable_night_mode(chat_id: int, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        cursor.execute("""UPDATE chats SET night_mode_status = ? WHERE id = ?""", (1, chat_id))
        conn.commit()


def disable_nigh_mode(chat_id: int, ):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        cursor.execute("""UPDATE chats SET night_mode_status = ? WHERE id = ?""", (0, chat_id))
        conn.commit()


###############

def get_report_chat(chat_id: int):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        data = cursor.execute("""SELECT report_chat FROM chats WHERE id = ?""", (chat_id,))
        return data.fetchone()[0]


def set_report_chat(chat_id: int, report_chat: int):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        cursor.execute("""UPDATE chats SET report_chat = ? WHERE id = ?""", (report_chat, chat_id))
        conn.commit()


###############

def get_auto_delete_commands_time(chat_id: int):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        data = cursor.execute("""SELECT auto_delete_commands_time FROM chats WHERE id = ?""", (chat_id,))
        return data.fetchone()[0]


def get_auto_delete_timetables_time(chat_id: int):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        data = cursor.execute("""SELECT auto_delete_timetables FROM chats WHERE id = ?""", (chat_id,))
        return data.fetchone()[0]


def set_auto_delete_commands_time(chat_id: int, seconds: int):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        cursor.execute("""UPDATE chats SET auto_delete_commands_time = ? WHERE id = ?""", (seconds, chat_id))
        conn.commit()


def set_auto_delete_timetables(chat_id: int, seconds: int):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        cursor.execute("""UPDATE chats SET auto_delete_timetables = ? WHERE id = ?""", (seconds, chat_id))
        conn.commit()


###############
###############
###############

def add_warn(chat_id: int, user_id: int, text: str):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        warns = cursor.execute("""SELECT warns FROM warns WHERE chat_id = ? and user_id = ?""",
                               (chat_id, user_id)).fetchone()
        if warns is None:
            cursor.execute("""INSERT INTO warns VALUES (?, ?, ?)""", (chat_id, user_id, text))
            conn.commit()
            return 1
        elif warns[0] == '':
            warns = []
        else:
            warns = warns[0].split(";;")
        warns.append(text)
        cursor.execute("""UPDATE warns SET warns = ? WHERE chat_id = ? and user_id = ?""",
                       (';;'.join(warns), chat_id, user_id))
        conn.commit()
        return len(warns)


def del_warn(chat_id: int, user_id: int, num: int):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        warns = cursor.execute("""SELECT warns FROM warns WHERE chat_id = ? and user_id = ?""",
                               (chat_id, user_id)).fetchone()
        if warns is None:
            cursor.execute("""INSERT INTO warns VALUES (?, ?, ?)""", (chat_id, user_id, ''))
            conn.commit()
            return False

        elif warns[0] == '':
            return False
        else:
            warns = warns[0].split(";;")
        if num <= 0 or num > len(warns):
            return False
        else:
            warns.pop(num - 1)
        cursor.execute("""UPDATE warns SET warns = ? WHERE chat_id = ? and user_id = ?""",
                       (';;'.join(warns), chat_id, user_id))
        conn.commit()
        return True


def get_warns(chat_id: int, user_id: int):
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        warns = cursor.execute("""SELECT warns FROM warns WHERE chat_id = ? and user_id = ?""",
                               (chat_id, user_id)).fetchone()
        if warns is None:
            cursor.execute("""INSERT INTO warns VALUES (?, ?, ?)""", (chat_id, user_id, ''))
            conn.commit()
            return []
        elif warns[0] == '':
            return []
        else:
            warns = warns[0].split(';;')
            return warns


##################

def get_all_users():
    with sqlite3.connect(os.path.join('data', "data.db")) as conn:
        cursor = conn.cursor()
        users = cursor.execute("""SELECT id FROM users""").fetchall()
        data = []
        for each in users:
            data.append(each[0])
        return data
