from loguru import logger
from pyrogram import filters
from pyrogram import Client
import config


@Client.on_message(filters.chat(config.chat_dp_id) & (filters.voice | filters.audio | filters.sticker | filters.animation | filters.game | filters.location))
async def delete_sticker_voice_audio_animation_game_location(app, message):
	try:
		if message.sticker:
			logger.info(f'user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | send sticker')
		elif message.voice:
			logger.info(f'user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | send voice')
		elif message.audio:
			logger.info(f'user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | send audio')
		elif message.animation:
			logger.info(f'user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | send animation')
		elif message.game:
			logger.info(f'user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | send game')
		elif message.location:
			logger.info(f'user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | send location')
		await message.delete()
	except Exception as e:
		print(e)