# Don't Remove Credit @P_World_18, @I_am_Never_die
# Ask Doubt on telegram @Upcoming

import asyncio
import os
import random
import sys
import re
import time
import aiohttp
from datetime import datetime, timedelta
from urllib.parse import quote
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatInviteLink, ChatPrivileges
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import *
from config import MSG_EFFECT
from helper_func import *
from database.database import *
from database.db_premium import *


BAN_SUPPORT = f"{BAN_SUPPORT}"
TUT_VID = f"{TUT_VID}"

# =================================================================== #
# 🔥 Short URL Generator + Click Counter
# =================================================================== #

API_URL = os.getenv("API_URL", "").rstrip("/")
if not API_URL:
    raise ValueError("⚠️ Missing 'API_URL' in Render environment variables!")


async def get_total_clicks(user_id, link):
    encoded_link = quote(link, safe="")
    api_url = f"{API_URL}/get_clicks?user_id={user_id}&link={encoded_link}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("total_clicks", 0)
            return 0


async def short_url(client: Client, message: Message, base64_string):
    try:
        user_id = message.from_user.id

        prem_link = f"https://t.me/{client.username}?start=yu3elk{base64_string}7"
        encoded_link = quote(prem_link, safe="")

        counter_url = f"{API_URL}/redirect?user_id={user_id}&link={encoded_link}"

        short_link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, counter_url)

        total_clicks = await get_total_clicks(user_id, prem_link)

        buttons = [
            [
                InlineKeyboardButton(text="ᴅᴏᴡɴʟᴏᴀᴅ", url=short_link),
                InlineKeyboardButton(text="ᴛᴜᴛᴏʀɪᴀʟ", url=TUT_VID),
            ],
            [InlineKeyboardButton(text="ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")],
        ]

        caption = f"Total Clicks :- {total_clicks}\n\n{SHORT_MSG.format()}"

        await message.reply_photo(
            photo=SHORTENER_PIC,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(buttons),
            message_effect_id=MSG_EFFECT
        )

    except Exception as e:
        import traceback
        traceback.print_exc() 
        print(f"❌ Error in short_url: {e}")
        # Ye line bot par asli error message degi
        await message.reply_text(f"⚠️ Error Details:\n`{e}`")


# =================================================================== #
# 🔥 START COMMAND FINAL FIX — OWNER BYPASS & HYBRID LINK SUPPORT
# =================================================================== #



# Note: Make sure helper_func.py has 'not_joined' function defined or imported.
# Agar 'not_joined' error de, to use 'start.py' ke andar define karna padega ya import karna padega.
async def not_joined(client, message):
    buttons = [
        [InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink)],
        [InlineKeyboardButton(text="ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{client.username}?start={message.command[1]}")]
    ]
    try:
        buttons.append([InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink2)])
    except: pass
    
    await message.reply(
        text="<b>ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀᴄᴄᴇss ᴛʜɪs ғɪʟᴇ.</b>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# =================================================================== #
# 🔥 not_joined()
# =================================================================== #

chat_data_cache = {}


async def not_joined(client: Client, message: Message):

    temp = await message.reply("<b><i>ᴄʜᴇᴄᴋɪɴɢ sᴜʙsᴄʀɪᴘᴛɪᴏɴ...</i></b>")
    uid = message.from_user.id

    buttons = []
    count = 0

    try:
        channels = await db.show_channels()

        for chat_id in channels:
            mode = await db.get_channel_mode(chat_id)

            if not await is_sub(client, uid, chat_id):

                try:
                    if chat_id not in chat_data_cache:
                        chat_data_cache[chat_id] = await client.get_chat(chat_id)

                    data = chat_data_cache[chat_id]

                    if mode == "on" and not data.username:
                        invite = await client.create_chat_invite_link(
                            chat_id=chat_id,
                            creates_join_request=True,
                            expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY)
                        )
                        link = invite.invite_link
                    else:
                        if data.username:
                            link = f"https://t.me/{data.username}"
                        else:
                            invite = await client.create_chat_invite_link(
                                chat_id=chat_id,
                                expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY)
                            )
                            link = invite.invite_link

                    buttons.append([InlineKeyboardButton(text=data.title, url=link)])
                    count += 1
                    await temp.edit(f"<b>{'! ' * count}</b>")

                except Exception as e:
                    print(e)
                    return await temp.edit(
                        f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @I_am_nerev_die</i></b>\n"
            f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
)
        # Try Again
        try:
            buttons.append(
                [
                    InlineKeyboardButton(
                        "♻️ Try Again",
                        url=f"https://t.me/{client.username}?start={message.command[1]}"
                    )
                ]
            )
        except:
            pass

        await message.reply_photo(
            FORCE_PIC,
            caption=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            message_effect_id=MSG_EFFECT
        )
        
    except Exception as e:
        print(e)
        await temp.edit(f"<b>Error Occurred:</b> {e}")

# =================================================================== #
# 🔥 Premium + Commands + Count (UNCHANGED)
# =================================================================== #

@Bot.on_message(filters.command('myplan') & filters.private)
async def check_plan_cmd(client, message):
    user_id = message.from_user.id
    status = await check_user_plan(user_id)
    await message.reply(status)


@Bot.on_message(filters.command('addpremium') & filters.private & admin)
async def add_premium_user_command(client, msg):
    if len(msg.command) != 4:
        return await msg.reply(
            "Usage: /addpremium <user_id> <value> <unit>\nUnits: s/m/h/d/y"
        )

    try:
        user_id = int(msg.command[1])
        value = int(msg.command[2])
        unit = msg.command[3].lower()

        expires = await add_premium(user_id, value, unit)

        await msg.reply(f"Added premium for {user_id}\nExpires: {expires}")

        await client.send_message(
            user_id,
            f"🎉 Premium Activated!\nDuration: {value}{unit}\nExpires: {expires}"
        )

    except Exception as e:
        await msg.reply(str(e))


@Bot.on_message(filters.command('remove_premium') & filters.private & admin)
async def remove_premium_cmd(client, msg):
    if len(msg.command) != 2:
        return await msg.reply("Usage: /remove_premium user_id")
    try:
        user = int(msg.command[1])
        await remove_premium(user)
        await msg.reply("Removed.")
    except:
        await msg.reply("Invalid ID")


@Bot.on_message(filters.command('premium_users') & filters.private & admin)
async def list_premium(client, message):

    ist = timezone("Asia/Kolkata")
    users = collection.find({})
    final = ["Active Premium Users:\n"]

    now = datetime.now(ist)

    async for user in users:
        uid = user["user_id"]
        exp = datetime.fromisoformat(user["expiration_timestamp"]).astimezone(ist)

        remain = exp - now
        if remain.total_seconds() <= 0:
            await collection.delete_one({"user_id": uid})
            continue

        u = await client.get_users(uid)
        d = f"{remain.days}d {remain.seconds//3600}h {(remain.seconds//60)%60}m"

        final.append(
            f"ID: <code>{uid}</code>\nUser: @{u.username}\nName:{u.mention}\nLeft: {d}\n"
        )

    await message.reply("\n".join(final), parse_mode=None)


@Bot.on_message(filters.command("count") & filters.private & admin)
async def count_cmd(client, message):
    c = await db.get_total_verify_count()
    await message.reply(f"Total Verified Tokens Today: <b>{c}</b>")


@Bot.on_message(filters.command('commands') & filters.private & admin)
async def admin_cmd(client, message):
    await message.reply(
        text=CMD_TXT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("• Close •", callback_data="close")]]),
        quote=True
                        )

#======================================================== The End =============================================================#
