import json
import os
import re

from apscheduler.jobstores.base import JobLookupError
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter, ChatType
from pyrogram.types import Message

import config
import costum_filters
import db
from func import auto_delete
from func import logger
from keyboards import inline
from schedulers import on_night_mode, night_mode_scheduler, off_night_mode

settings_commands = {
    "admins": ["[add или del] [теги юзеров разделяя ;]"],
    "night_mode": ["[start или stop] [зачение]", "[enable или disable]"],
    "links_whitelist": ["[add или del] [зачения разделяя ;]", "[enable или disable]"],
    "blacklist": ["[add или del] [зачения разделяя ;]"],
    "report": ["[тег или id группы или юзера (0 = всем администраторам)]"],
    "auto_delete": ["[command или timetable] [время в сек]"]
}


@Client.on_message(
    filters.command('settings', prefixes=config.prefix) & costum_filters.group & costum_filters.chat_admin_filter & costum_filters.admin_command)
async def change_settings(app: Client, message: Message):
    
    db.add_chat(message.chat.id, [(i.user.id if i.status == ChatMemberStatus.OWNER else ...) async for i in
                                  app.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS)])
    if len(message.command) < 2:
        logger.loggers(message, text="used !settings incorrectly")
        mes = await message.reply("Вы не указали аргументы\n/help для показа всех команд")
        await auto_delete.delete_command([mes, message])
        return
    if message.command[1] not in list(settings_commands):
        logger.loggers(message, text="used !settings command missing")
        mes = await message.reply("Такой настройки нет\n/help для показа всех команд")
        await auto_delete.delete_command([mes, message])
        return

    command = message.command[1]
    args = message.text.split(maxsplit=3)[1:]
    if command == 'admins' and len(message.text.split(maxsplit=2)) >= 3:
        if args[1] == 'add':
            admins = args[2].replace(" ", "").split(";")
            admin_list = []
            for i in admins:
                try:
                    admin = (await app.get_users(i)).id
                    admin_list.append(admin)
                except Exception:
                    pass
            for admin in admin_list:
                try:
                    db.add_admin(message.chat.id, admin)
                except Exception as e:
                    print(e)
            logger.loggers(message, text="Admins added successfully")
            await message.reply("Админы успешно добавлены")
            return
        elif args[1] == 'del':
            admins = args[2].replace(" ", "").split(";")
            admin_list = []
            for i in admins:
                try:
                    admin = (await app.get_users(i)).id
                    admin_list.append(admin)
                except Exception:
                    pass
            for admin in admin_list:
                if admin == message.from_user.id:
                    continue
                db.del_admin(message.chat.id, admin)
            logger.loggers(message, text="Admins successfully deleted")
            await message.reply("Админы успешно удалены")
            return
        elif args[1] == 'get':
            admins = db.get_chat_admins(message.chat.id, int_list=True)
            admin_list = []
            for i in admins:
                try:
                    admin = await app.get_users(i)
                    if admin.username:
                        admin_list.append(f"@{admin.username}")
                    else:
                        admin_list.append(
                            f"{admin.first_name} {admin.last_name or '- ' + '<code>' + str(admin.id) + '/code'}")
                except Exception:
                    pass
            await app.send_message(message.from_user.id, "Администраторы:\n" + '\n'.join(admin_list))
            mes = await message.reply("Отправил вам в лс")
            await auto_delete.delete_command([mes, message])
            return
        else:
            mes = await message.reply(
                f"Неверные аргументы\n<code>!settings {command} {' '.join(settings_commands.get(command))}</code>")
            await auto_delete.delete_command([mes, message])
            return
    elif command == 'night_mode' and len(message.text.split(maxsplit=2)) >= 3:
        if args[1] == 'start' or args[1] == 'stop':
            time = re.split(" |:|\.", args[2])
            for i in time:
                if not i.isdigit():
                    mes = await message.reply("Время в неправильном формате")
                    await auto_delete.delete_command([mes, message])
                    return
            if len(time) != 1 and 0 <= int(time[0]) < 24 and 0 <= int(time[1]) < 60:
                time = ' '.join([time[0], time[1]])
            elif len(time) == 1 and 0 <= int(time[0]) < 24:
                time = ' '.join([time[0], '0'])
            else:
                mes = await message.reply("Время в неправильном формате")
                await auto_delete.delete_command([mes, message])
                return
            db.change_night_mode_time(message.chat.id, args[1], time)
            try:
                night_mode_scheduler.reschedule_job(f'{message.chat.id}_{args[1]}', trigger='cron',
                                                    hour=time.split()[0], minute=time.split()[1])
            except JobLookupError:
                mes = await message.reply("Время изменено, но у вас не включен ночной режим")
                await auto_delete.delete_command([mes, message])
                return
            mes = await message.reply("Время изменено")
            await auto_delete.delete_command([mes, message])
            return
        elif args[1] == 'enable':
            db.enable_night_mode(message.chat.id)
            time = db.get_night_mode(message.chat.id)
            night_mode_scheduler.add_job(on_night_mode, "cron", args=(message.chat.id, app),
                                         name=f"{message.chat.id}_on",
                                         hour=time[0].split()[0], minute=time[0].split()[1])
            night_mode_scheduler.add_job(off_night_mode, "cron", args=(message.chat.id, app),
                                         name=f"{message.chat.id}_off",
                                         hour=time[1].split()[0], minute=time[1].split()[1])

        elif args[1] == 'disable':
            db.disable_nigh_mode(message.chat.id)
            try:
                night_mode_scheduler.remove_job(f"{message.chat.id}_on")
                night_mode_scheduler.remove_job(f"{message.chat.id}_off")
            except Exception as e:
                pass
            with open(os.path.join("data", "night_messages.json"), "r") as f:
                message_ids = json.load(f)
            message_ids.pop(message.chat.id, None)
            with open(os.path.join("data", "night_messages.json"), "w") as f:
                json.dump(message_ids, f)
        elif args[1] == 'get':
            time = db.get_night_mode(message.chat.id)
            await app.send_message(message.from_user.id,
                                   f"<b>Смена ночного режима</b>\nСтатус: {'включено' if bool(time[2]) else 'отключено'}\nВремя включения: {time[0].replace(' ', ':')}\n Время отключения: {time[1].replace(' ', ':')}")
            mes = await message.reply("Отправил вам в лс")
            await auto_delete.delete_command([mes, message])
            return
        else:
            mes = await message.reply(
                f"Неверные аргументы\n<code>!settings {command} {' '.join(settings_commands.get(command))}</code>")
            await auto_delete.delete_command([mes, message])
            return
    elif command == 'links_whitelist' and len(message.text.split(maxsplit=2)) >= 3:
        if args[1] == 'add':
            links = args[2].split(';')
            for link in links:
                db.add_link_to_whitelist(message.chat.id, link)
            mes = await message.reply("Ссылки успешно добавлены")
            await auto_delete.delete_command([mes, message])
            return
        elif args[1] == 'del':
            links = args[2].split(';')
            for link in links:
                db.del_link_from_whitelist(message.chat.id, link)
            mes = await message.reply("Ссылки успешно удалены")
            await auto_delete.delete_command([mes, message])
            return
        elif args[1] == 'enable':
            db.enable_links_whitelist_mode(message.chat.id)
            mes = await message.reply("Включено")
            await auto_delete.delete_command([mes, message])
            return
        elif args[1] == 'disable':
            db.disable_links_whitelist_mode(message.chat.id)
            mes = await message.reply("Отключено")
            await auto_delete.delete_command([mes, message])
            return
        elif args[1] == 'get':
            links = db.get_chat_links_whitelist(message.chat.id)
            links_list = []
            for i in links:
                links_list.append(f"<code>{i}</code>")
            status = db.get_links_whitelist_status(message.chat.id)
            await app.send_message(message.from_user.id,
                                   f"<b>Разрешённые ссылки</b>\nСтатус: {'Включено' if status else 'Отключено'}\n" + '\n'.join(
                                       links_list))
            mes = await message.reply("Отправил вам в лс")
            await auto_delete.delete_command([mes, message])
            return
        else:
            mes = await message.reply(
                f"Неверные аргументы\n<code>!settings {command} {' '.join(settings_commands.get(command))}</code>")
            await auto_delete.delete_command([mes, message])
            return
    elif command == 'blacklist' and len(message.text.split(maxsplit=2)) >= 3:
        if args[1] == 'add':
            words = args[2].split(';')
            for word in words:
                db.add_word_to_blacklist(message.chat.id, word)
            mes = await message.reply("Слова успешно добавлены")
            await auto_delete.delete_command([mes, message])
            return
        elif args[1] == 'del':
            words = args[2].split(';')
            for word in words:
                db.del_word_from_blacklist(message.chat.id, word)
            mes = await message.reply("Слова успешно удалены")
            await auto_delete.delete_command([mes, message])
            return
        elif args[1] == 'clean':
            pass
        elif args[1] == 'get':
            words = db.get_chat_blacklist(message.chat.id)
            words_list = []
            for i in words:
                words_list.append(f"<code>{i}</code>")
            await app.send_message(message.from_user.id, f"<b>Запрещённые слова</b>\n" + '\n'.join(words_list))
            mes = await message.reply("Отправил вам в лс")
            await auto_delete.delete_command([mes, message])
            return
        else:
            mes = await message.reply(f"Неверные аргументы\n<code>!settings {command} {' '.join(settings_commands.get(command))}</code>")
            await auto_delete.delete_command([mes, message])
            return
    elif command == "report" and len(message.text.split(maxsplit=2)) >= 3:
        if args[1] == 'get':
            chat = db.get_report_chat(message.chat.id)
            if chat == 0:
                chat = "Отправка всей администрации"
            else:
                chat = await app.get_chat(chat)
                chat = '@'+chat.username if chat.username else chat.id
            await app.send_message(message.from_user.id, f"Чат для отправки репортов:\n{chat}")
            mes = await message.reply("Отправил вам в лс")
            await auto_delete.delete_command([mes, message])
            return
        else:
            if args[1] == str(0):
                db.set_report_chat(message.chat.id, 0)
            else:
                try:
                    chat = await app.get_chat(args[1])
                except Exception:
                    await message.reply("Неизвестный чат!")
                    return
                db.set_report_chat(message.chat.id, chat.id)
                mes = await message.reply("Успешно")
                await auto_delete.delete_command([mes, message])
                return
    elif command == "auto_delete" and len(message.text.split(maxsplit=2)) >= 3:
        if args[1] == "get":
            timetable = db.get_auto_delete_timetables_time(message.chat.id)
            commands_time = db.get_auto_delete_commands_time(message.chat.id)
            await app.send_message(message.from_user.id, f"<b>Атоудаление:</b>\nРасписания: {'никогда' if timetable == 0 else str(timetable)+'сек'}\nКоманд: {'никогда' if timetable == 0 else str(commands_time)+'сек'}")
            mes = await message.reply("Отправил в лс")
            await auto_delete.delete_command([mes, message])
        else:
            if len(message.text.split()) >= 4 and args[2].isdigit():
                if args[1] == "command":
                    db.set_auto_delete_commands_time(message.chat.id, int(args[2]))
                    mes = await message.reply("Успешно")
                    await auto_delete.delete_command([mes, message])
                    return
                elif args[1] == "timetable":
                    db.set_auto_delete_timetables_time(message.chat.id, int(args[2]))
                    mes = await message.reply("Успешно")
                    await auto_delete.delete_command([mes, message])
                    return
                else:
                    mes = await message.reply(
                        f"Неверные аргументы\n<code>!settings {command} {' '.join(settings_commands.get(command))}</code>")
                    await auto_delete.delete_command([mes, message])
                    return
            else:
                mes = await message.reply(f"Неверные аргументы\n<code>!settings {command} {' '.join(settings_commands.get(command))}</code>")
                await auto_delete.delete_command([mes, message])
                return
    else:
        mes = await message.reply(
            f"Неверные аргументы\n<code>!settings {command} {' '.join(settings_commands.get(command))}</code>")
        await auto_delete.delete_command([mes, message])
        return


@Client.on_message(filters.command('help'))
async def help_message(app: Client, message: Message):
    mes = None
    if message.chat.type is not ChatType.PRIVATE:
        mes = await message.reply("Отправил в лс")
    text = []
    text.append("<b>Все команды для юзеров:</b>\n"
                "<code>!report</code> - отправляет сообщение, на которое вы ответили, администрации\n"
                "<code>!mail</code> - подписаться/отписаться на/от рассылки")
    text.append("\n<b>Все команды для администрации группы:</b>")
    for command in settings_commands:
        command_args = settings_commands.get(command)
        for i in command_args:
            text.append(f"<code>{config.prefix}settings {command} {i}</code>")
    text.append("Узнать значение любой настройки можно с помощью get\nПример: !settings [настройка] get")
    text.append("<code>!warn [причина]</code> - выдаёт юзеру варн и мут(1 варн - 3ч, 2 варн - 24ч, больше 3 варнов - 48ч)\n"
                "<code>!warn del [номер варна]</code> - удаляет варн\n"
                "<code>!info</code> показывает все варны юзера на чьё сообщение вы ответили\n"
                "<code>!add_admin [юзернеймы разделяя ;]</code> - добовляет юзера в администрацию чата(открывает доступ к командам выше)")
    if message.from_user.id in config.admins:
        text.append("\n<b>Команды для тех персонала:</b>")
        text.append("<code>/mailer [2 - без подписки, 1 - c подпиской, 0 - всем] [0 - оффициал канал, 1 - Оффициал Предствитель, 2 - Пустуо]</code>\n<code>/repair</code>\n<code>/parse</code>\n<code>/stop</code> - остановка бота\n<code>/send_log</code>\n<code>/stats</code> - статистика использований")
    if inline.donate_kb():
        text.append("\nВи можете надати гроші для сплати за сервер для роботи бота та підтримки адміністрації бота\n\n🔗Посилання на Банку\nhttps://send.monobank.ua/jar/6E85edaBFL\n\n💳Номер карти Банки\n<code>5375 4112 0229 7482</code>")
    await app.send_message(message.from_user.id, '\n'.join(text), reply_markup=inline.donate_kb())
    await auto_delete.delete_command([mes, message])
    return


@Client.on_message(filters.command("add_admin", prefixes=config.prefix) & costum_filters.chat_admin_filter & costum_filters.admin_command)
async def add_admin_func(app: Client, message: Message):
    if len(message.command) > 1:
        args = message.text.split(maxsplit=1)
        admins = args[0].replace(" ", "").split(";")
        admin_list = []
        for i in admins:
            try:
                admin = (await app.get_users(i)).id
                admin_list.append(admin)
            except Exception:
                pass
        for admin in admin_list:
            try:
                db.add_admin(message.chat.id, admin)
            except Exception as e:
                print(e)
        logger.loggers(message, text="Admins added successfully")
        mes = await message.reply("Админы успешно добавлены")
        await auto_delete.delete_command([mes, message])
        return
    else:
        mes = await message.reply("Вы не написали юзеров для добавления")
        await auto_delete.delete_command([mes, message])
        return