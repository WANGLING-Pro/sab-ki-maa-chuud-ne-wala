# Don't Remove Credit @P_World_18, @I_am_Never_die
# Ask Doubt on telegram @Upcoming

import asyncio
import os
import random
import sys
import re
import string 
import string as rohit
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatInviteLink, ChatPrivileges
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
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
        print(f"❌ Error ShortURL: {e}")
        await message.reply("⚠️ Something went wrong.")


# =================================================================== #
# 🔥 START COMMAND FIXED — AUTO SHORTENER DISABLED
# =================================================================== #

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):

    user_id = message.from_user.id
    is_premium = await is_premium_user(user_id)

    # BAN CHECK
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        return await message.reply_text(
            "<b>⛔️ You are Bᴀɴɴᴇᴅ from using this bot.</b>\n\n"
            "<i>Contact support if you think this is a mistake.</i>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Contact Support", url=BAN_SUPPORT)]]
            )
        )

    # FSUB
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    # File auto-delete time in seconds
    FILE_AUTO_DELETE = await db.get_del_timer()
    
    # NEW USER ADD
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except:
            pass

    # PAYLOAD HANDLE
    if message.text.startswith("/start ") and len(message.text.split(" ", 1)) == 2:

        try:
            basic = message.text.split(" ", 1)[1]

            # Non-premium → shortener
            if (not is_premium) and (user_id != OWNER_ID) and (not basic.startswith("yu3elk")):
                await short_url(client, message, basic)
                return

            # premium
            base64_string = basic[6:-1] if basic.startswith("yu3elk") else basic

        except Exception as e:
            print(f"Error payload: {e}")
            return

        # Decode
        string = await decode(base64_string)
        args = string.split("-")

        ids = []
        try:
            if len(args) == 3:
                start = int(int(args[1]) / abs(client.db_channel.id))
                end = int(int(args[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else range(start, end - 1, -1)

            elif len(args) == 2:
                ids = [int(int(args[1]) / abs(client.db_channel.id))]

        except Exception as e:
            print(f"Error decode id: {e}")
            return

        temp = await message.reply("<b>Please wait...</b>")

        try:
            msgs = await get_messages(client, ids)
        except:
            await message.reply("Something went wrong!")
            return
        finally:
            await temp.delete()

        sent_msgs = []

        for msg in msgs:
            original_caption = msg.caption.html if msg.caption else ""
            final_caption = f"{original_caption}\n\n{CUSTOM_CAPTION}" if CUSTOM_CAPTION else original_caption
            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                s = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=final_caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                await asyncio.sleep(0.5)
                sent_msgs.append(s)

            except FloodWait as e:
                await asyncio.sleep(e.x)
                s = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=final_caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                sent_msgs.append(s)

        # AUTO DELETE
        FILE_DEL = await db.get_del_timer()
        if FILE_DEL > 0:

            note = await message.reply(
                f"<b>Tʜɪs Fɪʟᴇ ᴡɪʟʟ ʙᴇ Dᴇʟᴇᴛᴇᴅ ɪɴ  {get_exp_time(FILE_AUTO_DELETE)}. Pʟᴇᴀsᴇ sᴀᴠᴇ ᴏʀ ғᴏʀᴡᴀʀᴅ ɪᴛ ᴛᴏ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ʙᴇғᴏʀᴇ ɪᴛ ɢᴇᴛs Dᴇʟᴇᴛᴇᴅ.</b>"
            ),
            message_effect_id=MSG_EFFECT
            )

            await asyncio.sleep(FILE_DEL)

            for s in sent_msgs:
                try:
                    await s.delete()
                except:
                    pass

            try:
                reload_url = (
                    f"https://t.me/{client.username}?start={message.command[1]}"
                    if message.command and len(message.command) > 1
                    else None
                )

                kb = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ", url=reload_url)]]
                ) if reload_url else None

                await note.edit(
                    "<b>ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ !!\n\nᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇</b>",
                    reply_markup=kb
                )

            except Exception as e:
                print(e)

        return

    # NORMAL START MESSAGE
    start_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("• ᴍᴏʀᴇ ᴄʜᴀɴɴᴇʟs •", url="https://t.me/P_World_81")],
            [
                InlineKeyboardButton("•ᴀʙᴏᴜᴛ", callback_data="about"),
                InlineKeyboardButton("•ʜᴇʟᴘ", callback_data="help"),
            ],
        ]
    )

    await message.reply_photo(
        photo=START_PIC,
        caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=start_markup,
        message_effect_id=5104841245755180586
    )


# =================================================================== #
# 🔥 not_joined()
# =================================================================== #

chat_data_cache = {}


async def not_joined(client: Client, message: Message):

    temp = await message.reply("<b><i>Checking Subscription...</i></b>")
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
