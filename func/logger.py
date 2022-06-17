
from loguru import logger
def loggers(message, text):
    logger.info(f'chat_id = {message.chat.id} | user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | {text}')

