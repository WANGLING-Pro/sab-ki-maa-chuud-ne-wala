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
from database.database import db
from database.db_premium import *


BAN_SUPPORT = f"{BAN_SUPPORT}"
TUT_VID = f"{TUT_VID}"

# =================================================================== #
# 🔥 Short URL Generator + Click Counter
# =================================================================== #

API_URL = os.getenv("API_URL", "").rstrip("/")
if not API_URL:
    raise ValueError("⚠️ Missing 'API_URL' in environment variables!")


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
        await message.reply_text(f"⚠️ Error Details:\n`{e}`")
        

# =================================================================== #
# 🔥 START COMMAND FIXED — AUTO SHORTENER DISABLED
# =================================================================== #

@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):

    user_id = message.from_user.id

# ======================
# BAN CHECK
# ======================

banned_users = await db.get_ban_users()

if user_id in banned_users:
    return await message.reply_text(
        "<b>⛔️ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ.</b>\n\n"
        "<i>ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ ɪғ ʏᴏᴜ ᴛʜɪɴᴋ ᴛʜɪs ɪs ᴀ ᴍɪsᴛᴀᴋᴇ.</i>",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ", url=BAN_SUPPORT)]]
        )
    )
    
    # ======================
    # FORCE SUB
    # ======================
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    # ======================
    # ADD USER
    # ======================
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except:
            pass

    # ======================
    # NORMAL /start (NO PAYLOAD)
    # ======================
    if len(message.command) == 1:
        start_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("• ᴍᴏʀᴇ ᴄʜᴀɴɴᴇʟs •", url="https://t.me/P_World_81")],
                [
                    InlineKeyboardButton("•ᴀʙᴏᴜᴛ", callback_data="about"),
                    InlineKeyboardButton("•ʜᴇʟᴘ", callback_data="help"),
                ],
            ]
        )

        return await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=user_id
            ),
            reply_markup=start_markup,
            message_effect_id=MSG_EFFECT
        )

    # ======================
    # PAYLOAD MODE
    # ======================

    is_premium = await is_premium_user(user_id)

    try:
        payload = message.command[1]

        # Non premium -> shortener
        if (not is_premium) and (user_id != OWNER_ID) and (not payload.startswith("yu3elk")):
            await short_url(client, message, payload)
            return

        # unwrap premium wrapper
        base64_string = payload[6:-1] if payload.startswith("yu3elk") else payload

        decoded = await decode(base64_string)
        args = decoded.split("-")

        ids = []

        if len(args) == 3:
            start = int(int(args[1]) / abs(client.db_channel.id))
            end = int(int(args[2]) / abs(client.db_channel.id))
            step = 1 if start <= end else -1
            ids = list(range(start, end + step, step))

        elif len(args) == 2:
            ids = [int(int(args[1]) / abs(client.db_channel.id))]

        else:
            return await message.reply("❌ Invalid or expired link.")

    except Exception as e:
        print("Payload error:", e)
        return await message.reply("❌ Invalid or expired link.")

    # ======================
    # FETCH FILES
    # ======================

    temp = await message.reply("<b>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... ғᴇᴛᴄʜɪɴɢ ғɪʟᴇs...</b>")

    try:
        msgs = await get_messages(client, ids)
    except Exception as e:
        print("Get messages error:", e)
        await temp.delete()
        return await message.reply("❌ ғɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ!")
    finally:
        try:
            await temp.delete()
        except:
            pass

    sent_msgs = []

    for msg in msgs:
        if not msg or msg.empty:
            continue

        original_caption = msg.caption.html if msg.caption else ""
        final_caption = f"{original_caption}\n\n{CUSTOM_CAPTION}" if CUSTOM_CAPTION else original_caption
        reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

        try:
            s = await msg.copy(
                chat_id=user_id,
                caption=final_caption,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                protect_content=PROTECT_CONTENT
            )
            sent_msgs.append(s)
            await asyncio.sleep(0.4)

        except FloodWait as e:
            await asyncio.sleep(e.x)
            try:
                s = await msg.copy(
                    chat_id=user_id,
                    caption=final_caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                sent_msgs.append(s)
            except:
                pass

        except Exception as e:
            print("Copy error:", e)
            continue

    # ======================
    # AUTO DELETE SYSTEM
    # ======================

    FILE_DEL = await db.get_del_timer()

    if FILE_DEL and FILE_DEL > 0 and sent_msgs:

        note = await message.reply(
            text=(
                f"Tʜɪs Fɪʟᴇ ᴡɪʟʟ ʙᴇ Dᴇʟᴇᴛᴇᴅ ɪɴ {get_exp_time(FILE_DEL)}. "
                "Pʟᴇᴀsᴇ sᴀᴠᴇ ᴏʀ ғᴏʀᴡᴀʀᴅ ɪᴛ ᴛᴏ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ʙᴇғᴏʀᴇ ɪᴛ ɢᴇᴛs Dᴇʟᴇᴛᴇᴅ."
            ),
            message_effect_id=MSG_EFFECT
        )

        await asyncio.sleep(FILE_DEL)

        for s in sent_msgs:
            try:
                await s.delete()
            except:
                pass

        reload_url = f"https://t.me/{client.username}?start={message.command[1]}"

        kb = InlineKeyboardMarkup(
            [[InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ", url=reload_url)]]
        )

        try:
            await note.edit(
                text=(
                    "ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ !!\n\n"
                    "ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇"
                ),
                reply_markup=kb
            )
        except:
            pass

    return    
                
    

#•••••••••••••••••••••••••••••••••••••••••••••••••••• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •••••••••••••••••••••••••••••••••••••••••#
from datetime import datetime, timedelta
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

chat_data_cache = {}

async def not_joined(client: Client, message: Message):

    uid = message.from_user.id

    # Payload for Try Again button
    payload = None
    if message.command and len(message.command) > 1:
        payload = message.command[1]

    temp = await message.reply("<b><i>ᴄʜᴇᴄᴋɪɴɢ sᴜʙsᴄʀɪᴘᴛɪᴏɴ...</i></b>")

    buttons = []

    try:
        channels = await db.show_channels()

        for chat_id in channels:
            # Check membership
            try:
                member = await client.get_chat_member(chat_id, uid)
                if member.status in (
                    ChatMemberStatus.MEMBER,
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.OWNER
                ):
                    continue
            except:
                pass

            # Cache chat
            if chat_id not in chat_data_cache:
                chat_data_cache[chat_id] = await client.get_chat(chat_id)

            chat = chat_data_cache[chat_id]
            mode = await db.get_channel_mode(chat_id)

            # Generate link
            if chat.username:
                link = f"https://t.me/{chat.username}"
            else:
                if mode == "on":
                    invite = await client.create_chat_invite_link(
                        chat_id=chat_id,
                        creates_join_request=True,
                        expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY)
                    )
                else:
                    invite = await client.create_chat_invite_link(
                        chat_id=chat_id,
                        expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY)
                    )
                link = invite.invite_link

            buttons.append([
                InlineKeyboardButton(text=f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ {chat.title}", url=link)
            ])

        # Try again button
        if payload:
            retry_url = f"https://t.me/{client.username}?start={payload}"
        else:
            retry_url = f"https://t.me/{client.username}"

        buttons.append([
            InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ", url=retry_url)
        ])

        await temp.delete()

        await message.reply_photo(
            photo=FORCE_PIC,
            caption=(
                "<blockquote expandable>"
                "ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴀʟʟ ʀᴇǫᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟs ᴛᴏ ᴀᴄᴄᴇss ᴛʜɪs ғɪʟᴇ.\n\n"
                "ᴊᴏɪɴ ᴀʟʟ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ \"Try Again\"."
                "</blockquote>"
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            message_effect_id=MSG_EFFECT
        )

    except Exception as e:
        print("FSUB ERROR:", e)

        # Owner ko notify kar
        try:
            await client.send_message(
                OWNER_ID,
                f"⚠️ FSUB ERROR:\n<code>{e}</code>"
            )
        except:
            pass

        try:
            await temp.edit(
                f"<blockquote expandable><b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @I_am_nerev_die</i></b></blockquote>\n"
            f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
            )
        except:
            pass



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
