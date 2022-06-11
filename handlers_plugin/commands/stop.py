import sys
from pyrogram import filters
from pyrogram import Client
import config


@Client.on_message(filters.command("stop", prefixes=config.prefix) & filters.user(config.default_admins))
async def stop(app, message):
    sys.exit(0)
