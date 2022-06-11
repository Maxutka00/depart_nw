import sqlite3
from loguru import logger
from pyrogram import filters
from pyrogram import enums
from pyrogram import Client
import conf



@Client.on_message(filters.command("del_time", prefixes="!") & filters.user([29764093,594165498,1398764450]))
async def del_time(сlient, message):
	logger.info(f'user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | used !del_time')
	conn = sqlite3.connect("./base_date/transp_inf.db")
	cur = conn.cursor()
	msg = message.text.html.split(" ", 1)
	Re = cur.execute('SELECT temes FROM delet_times').fetchone()
	if Re is None:
		cur.execute("""INSERT INTO delet_times(temes) VALUES(?);""", (int(msg[1]),))
	else:
		cur.execute("""UPDATE delet_times SET temes=?""", (int(msg[1]),))
	conn.commit()
	Result = cur.execute('SELECT temes FROM delet_times').fetchone()
	await сlient.send_message(message.chat.id,f"Установлено время авто-удаление сообщений:\n{str(Result[0])} минут\n\n если что-то не правильно отправте еще раз !del_time",parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)
	conn.close()