from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot import Bot
from config import *
from helper_func import *
from database.database import db

# =================================================================================== #
# BOT STATS COMMAND
# =================================================================================== #

@Bot.on_message(filters.command('stats') & admin)
async def stats(bot: Bot, message: Message):
    try:
        now = datetime.now()
        delta = now - bot.uptime
        uptime_str = get_readable_time(int(delta.total_seconds()))

        await message.reply_text(
            text=BOT_STATS_TEXT.format(uptime=uptime_str),
            quote=True
        )
    except Exception as e:
        await message.reply_text(f"❌ <b>Error fetching stats:</b>\n<code>{e}</code>", quote=True)


# =================================================================================== #
# USER COUNT COMMAND
# =================================================================================== #

WAIT_MSG = "<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</i></b>"

@Bot.on_message(filters.command('users') & filters.private & admin)
async def get_users(client: Bot, message: Message):
    msg = await message.reply_text(WAIT_MSG, quote=True)

    try:
        users = await db.full_userbase()
        user_count = len(users) if users else 0
        await msg.edit_text(
            f"<b>📊 Total Bot Users:</b> <code>{user_count}</code>"
        )
    except Exception as e:
        await msg.edit_text(f"❌ <b>Error fetching users:</b>\n<code>{e}</code>")


# =================================================================================== #
# AUTO DELETE TIMER COMMANDS
# =================================================================================== #

@Bot.on_message(filters.command('dlt_time') & filters.private & admin)
async def set_delete_time(client: Bot, message: Message):
    try:
        if len(message.command) < 2:
            return await message.reply_text(
                "<b>⚠️ Usage:</b> <code>/dlt_time <seconds></code>\n"
                "<b>Example:</b> <code>/dlt_time 300</code> (for 5 mins)",
                quote=True
            )

        duration = int(message.command[1])

        if duration <= 0:
            return await message.reply_text("❌ <b>Duration must be greater than 0 seconds.</b>", quote=True)

        await db.set_del_timer(duration)

        readable_time = get_readable_time(duration) if 'get_readable_time' in globals() else f"{duration} seconds"

        await message.reply_text(
            f"✅ <b>Delete Timer updated successfully!</b>\n\n"
            f"<blockquote><b>New Duration:</b> <code>{duration} seconds</code> ({readable_time})</blockquote>",
            quote=True
        )

    except ValueError:
        await message.reply_text(
            "<b>❌ Invalid number! Please provide time in seconds as an integer.</b>\n"
            "<b>Usage:</b> <code>/dlt_time 60</code>",
            quote=True
        )
    except Exception as e:
        await message.reply_text(f"❌ <b>Error setting timer:</b>\n<code>{e}</code>", quote=True)


@Bot.on_message(filters.command('check_dlt_time') & filters.private & admin)
async def check_delete_time(client: Bot, message: Message):
    try:
        duration = await db.get_del_timer()
        
        if not duration or duration <= 0:
            msg_text = "<b>⚠️ Auto-delete timer is currently disabled or not set.</b>"
        else:
            readable_time = get_readable_time(duration) if 'get_readable_time' in globals() else f"{duration} seconds"
            msg_text = (
                f"<b>⏱ Current Delete Timer Settings:</b>\n\n"
                f"<blockquote><b>Duration:</b> <code>{duration} seconds</code> ({readable_time})</blockquote>"
            )

        await message.reply_text(msg_text, quote=True)

    except Exception as e:
        await message.reply_text(f"❌ <b>Error checking timer:</b>\n<code>{e}</code>", quote=True)
