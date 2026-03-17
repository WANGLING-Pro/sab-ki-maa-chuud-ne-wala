# =================================================================================== ##
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot import Bot
from config import *
from helper_func import *
from database.database import db

# =================================================================================== ##

@Bot.on_message(filters.command('stats') & admin)
async def stats(bot: Bot, message: Message):
    now = datetime.now()
    delta = now - bot.uptime
    uptime_str = get_readable_time(delta.seconds)

    await message.reply(BOT_STATS_TEXT.format(uptime=uptime_str))


# =================================================================================== ##

WAIT_MSG = "<b>Working....</b>"

# =================================================================================== ##

@Bot.on_message(filters.command('users') & filters.private & admin)
async def get_users(client: Bot, message: Message):
    msg = await message.reply(WAIT_MSG)

    try:
        users = await db.full_userbase()
        await msg.edit(f"{len(users)} users are using this bot")
    except Exception as e:
        await msg.edit(f"❌ Error fetching users:\n<code>{e}</code>")


# =================================================================================== ##
# AUTO DELETE TIMER
# =================================================================================== ##

@Bot.on_message(filters.private & filters.command('dlt_time') & admin)
async def set_delete_time(client: Bot, message: Message):
    try:
        duration = int(message.command[1])

        if duration <= 0:
            return await message.reply("❌ Duration must be greater than 0.")

        await db.set_del_timer(duration)

        await message.reply(
            f"<b>Dᴇʟᴇᴛᴇ Tɪᴍᴇʀ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴛᴏ <blockquote>{duration} seconds</blockquote></b>"
        )

    except (IndexError, ValueError):
        await message.reply(
            "<b>Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.</b>\nUsage: /dlt_time 60"
        )


@Bot.on_message(filters.private & filters.command('check_dlt_time') & admin)
async def check_delete_time(client: Bot, message: Message):
    try:
        duration = await db.get_del_timer()

        await message.reply(
            f"<b><blockquote>Cᴜʀʀᴇɴᴛ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ ɪs sᴇᴛ ᴛᴏ: {duration} seconds</blockquote></b>"
        )
    except Exception as e:
        await message.reply(f"❌ Error:\n<code>{e}</code>")

# =================================================================================== ##
