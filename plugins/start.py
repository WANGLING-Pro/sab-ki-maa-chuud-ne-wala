# ================= IMPORTS =================

import asyncio
import aiohttp
import os
import sys
import time
import traceback
from datetime import datetime, timedelta
from pytz import timezone

from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import (
    UserNotParticipant,
    InviteHashEmpty,
    ChatAdminRequired,
    PeerIdInvalid,
    UserIsBlocked,
    InputUserDeactivated
)

from bot import Bot
from config import *
from helper_func import *
from database.database import db
from database.db_premium import (
    is_premium_user,
    add_premium,
    remove_premium,
    remove_expired_users,
    check_user_plan,
    collection
)

# ================= GLOBALS =================

BAN_SUPPORT = f"{BAN_SUPPORT}"
TUT_VID = f"{TUT_VID}"
chat_data_cache = {}

# ================= RELAY GATE CONFIG =================

GATE_URL = getattr(__import__("config"), "GATE_URL", "https://your-relay-gate.onrender.com")
GATE_API_KEY = getattr(__import__("config"), "GATE_API_KEY", "")
BOT_SOURCE_NAME = getattr(__import__("config"), "BOT_SOURCE_NAME", "unknown_bot")


async def get_gate_link(real_url: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{GATE_URL}/api/generate",
                json={"url": real_url, "source": BOT_SOURCE_NAME},
                headers={"X-API-Key": GATE_API_KEY},
                timeout=aiohttp.ClientTimeout(total=8)
            ) as resp:
                data = await resp.json()
                verify_url = data.get("verify_url")
                if verify_url:
                    return verify_url
                print(f"GATE ERROR (bad response): {data}")
    except Exception as e:
        print(f"GATE ERROR (request failed): {e}")

    return real_url


# ================= SHORT URL FUNCTION =================

async def short_url(client: Client, message: Message, base64_string):
    try:
        username = client.me.username if client.me.username else "botusername"
        prem_link = f"https://t.me/{username}?start=yu3elk{base64_string}7"

        url, api = await db.get_shortener_config()
        url = url or SHORTLINK_URL
        api = api or SHORTLINK_API
        short_link = await get_shortlink(url, api, prem_link)

        gate_link = await get_gate_link(short_link)

        buttons = [
            [
                InlineKeyboardButton(text="ᴅᴏᴡɴʟᴏᴀᴅ", url=gate_link),
                InlineKeyboardButton(text="ᴛᴜᴛᴏʀɪᴀʟ", url=TUT_VID)
            ],
            [
                InlineKeyboardButton(text="ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")
            ]
        ]

        await message.reply_photo(
            photo=SHORTENER_PIC,
            caption=SHORT_MSG.format(),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except Exception as e:
        print(f"SHORT_URL ERROR = {e}")


# ================= FORCE SUB FUNCTION =================

async def not_joined(client: Client, message: Message):
    uid = message.from_user.id

    payload = None
    if message.command and len(message.command) > 1:
        payload = message.command[1]

    temp = await message.reply("<b><i>ᴄʜᴇᴄᴋɪɴɢ sᴜʙsᴄʀɪᴘᴛɪᴏɴ...</i></b>")
    buttons = []

    try:
        channels = await db.show_channels()

        for chat_id in channels:
            try:
                member = await client.get_chat_member(chat_id, uid)
                if member.status in (
                    ChatMemberStatus.MEMBER,
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.OWNER
                ):
                    continue
            except Exception:
                pass

            if chat_id not in chat_data_cache:
                chat_data_cache[chat_id] = await client.get_chat(chat_id)

            chat = chat_data_cache[chat_id]
            mode = await db.get_channel_mode(chat_id)

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
                InlineKeyboardButton(text=f"ᴊᴏɪɴ {chat.title}", url=link)
            ])

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
        print(f"FSUB ERROR: {e}")
        try:
            await client.send_message(
                OWNER_ID,
                f"⚠️ FSUB ERROR:\n<code>{e}</code>"
            )
        except Exception:
            pass

        try:
            await temp.edit(
                f"<blockquote expandable><b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ @I_am_nerev_die</i></b></blockquote>\n"
                f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
            )
        except Exception:
            pass


# ================= START COMMAND =================

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    try: 
        print("DB TYPE =", type(db))
        user_id = message.from_user.id
        print(f"[START] User {user_id} triggered start command")

        banned_users = await db.get_ban_users()
        print(f"[BAN CHECK] Banned users: {len(banned_users)}")

        if user_id in banned_users:
            print(f"[BAN] User {user_id} is banned")
            await message.reply_text(
                "<b>⛔️ You are Banned from using this bot.</b>\n\n"
                "<i>Contact support if you think this is a mistake.</i>",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Contact Support", url=BAN_SUPPORT)]]
                )
            )
            return

        print(f"[BAN CHECK] User {user_id} is NOT banned ✅")

    except Exception as e:
        print(f"[ERROR] Start command failed: {e}")
        traceback.print_exc()

    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    FILE_AUTO_DELETE = await db.get_del_timer()

    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except Exception:
            pass

    text = message.text

    if len(text) > 7:
        ids = None
        base64_string = None
        sent_msgs = []

        try:
            basic = text.split(" ", 1)[1]
            payload = basic

            print(f"PAYLOAD RECEIVED = {payload}")

            is_premium = await is_premium_user(user_id)
            shortener_status = await db.get_shortener_status()

            if shortener_status == "on" and not is_premium and user_id != OWNER_ID and not basic.startswith("yu3elk"):
                print(f"SHORTENER MODE TRIGGERED FOR USER {user_id}")
                await short_url(client, message, basic)
                return

            if basic.startswith("yu3elk"):
                print("Shortener format detected")
                base64_string = basic[6:-1]
            else:
                print("Normal payload format")
                base64_string = basic

            print(f"BASE64 STRING TO DECODE = {base64_string}")

            ids = await decode(base64_string)
            print(f"DECODE SUCCESS - IDS = {ids}, TYPE = {type(ids)}")

            argument = str(ids).split("-")
            ids = []

            if len(argument) == 3:
                try:
                    start = int(int(argument[1]) / abs(client.db_channel.id))
                    end = int(int(argument[2]) / abs(client.db_channel.id))
                    ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
                except Exception as e:
                    print(f"Error decoding IDs: {e}")
                    return

            elif len(argument) == 2:
                try:
                    ids = [int(int(argument[1]) / abs(client.db_channel.id))]
                except Exception as e:
                    print(f"Error decoding ID: {e}")
                    return

        except IndexError as ie:
            print(f"INDEX ERROR = {ie}")
            return await message.reply("❌ Invalid Command Format / No payload provided")

        except Exception as e:
            print(f"PAYLOAD ERROR = {e}")
            print(f"FULL TRACEBACK: {traceback.format_exc()}")
            return await message.reply(f"❌ Invalid Link or Format Error: {str(e)[:100]}")

        if not ids:
            print("IDS IS EMPTY - RETURNING")
            return await message.reply("❌ Failed to decode payload - IDs are empty")

        temp_msg = await message.reply("<b>⏳ Please wait...</b>")

        try:
            print(f"FETCH ATTEMPT - IDS: {ids}, TYPE: {type(ids)}")
            messages = await get_messages(client, ids)
            print(f"MESSAGES FETCHED = {len(messages) if messages else 0}")

            if not messages:
                await temp_msg.delete()
                return await message.reply("❌ File not found in Database")

        except Exception as fetch_err:
            print(f"FETCH ERROR = {fetch_err}")
            print(f"FETCH ERROR TRACEBACK: {traceback.format_exc()}")
            try:
                await temp_msg.delete()
            except Exception:
                pass
            return await message.reply(f"❌ File not found in Database\n\nError: {str(fetch_err)[:80]}")

        try:
            await temp_msg.delete()
        except Exception:
            pass

        for msg in messages:
            if not msg or msg.empty:
                continue

            try:
                original_caption = msg.caption.html if msg.caption else ""
                caption = f"{original_caption}\n\n{CUSTOM_CAPTION}" if CUSTOM_CAPTION else original_caption

                s = await msg.copy(
                    chat_id=user_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    protect_content=PROTECT_CONTENT,
                    reply_markup=None
                )
                sent_msgs.append(s)
                await asyncio.sleep(0.4)

            except FloodWait as e:
                await asyncio.sleep(e.x)
                try:
                    s = await msg.copy(
                        chat_id=user_id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        protect_content=PROTECT_CONTENT,
                        reply_markup=None
                    )
                    sent_msgs.append(s)
                except Exception:
                    pass

            except Exception:
                continue

        FILE_DEL = await db.get_del_timer()

        if FILE_DEL and FILE_DEL > 0 and sent_msgs:
            note = await message.reply(
                f"<b>File will be deleted in {get_exp_time(FILE_DEL)}</b>"
            )

            await asyncio.sleep(FILE_DEL)

            for s in sent_msgs:
                try:
                    await s.delete()
                except Exception:
                    pass

            try:
                await note.edit("File deleted.")
            except Exception:
                pass

    else:
        start_buttons = [
            [InlineKeyboardButton("• ᴍᴏʀᴇ ᴄʜᴀɴɴᴇʟs •", url="https://t.me/P_World_81")],
            [
                InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
                InlineKeyboardButton('ʜᴇʟᴘ •', callback_data="help")
            ]
        ]

        if user_id == OWNER_ID or await db.admin_exist(user_id):
            start_buttons.append(
                [InlineKeyboardButton("⚙️ ꜱʜᴏʀᴛᴇɴᴇʀ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="shortener_menu")]
            )

        reply_markup = InlineKeyboardMarkup(start_buttons)

        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name or "",
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            message_effect_id=5104841245755180586
        )

        return

# ================= ADMIN COMMANDS =================

@Bot.on_message(filters.command('add_admin') & filters.private & filters.user(OWNER_ID))
async def add_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    try:
        admin_ids = await db.get_all_admins() or []
        admins = message.text.split()[1:]

        if not admins:
            return await pro.edit(
                "<b>You need to provide user ID(s) to add as admin.</b>\n\n"
                "<b>Usage:</b>\n"
                "<code>/add_admin [user_id]</code> — Add one or more user IDs\n\n"
                "<b>Example:</b>\n"
                "<code>/add_admin 1234567890 9876543210</code>",
                reply_markup=reply_markup
            )

        admin_list = ""
        for user_id in admins:
            try:
                valid_id = int(user_id)
            except ValueError:
                admin_list += f"<blockquote><b>Invalid ID: <code>{user_id}</code></b></blockquote>\n"
                continue

            if valid_id in admin_ids:
                admin_list += f"<blockquote><b>ID <code>{valid_id}</code> already exists.</b></blockquote>\n"
                continue

            await db.add_admin(valid_id)
            admin_list += f"<b><blockquote>(ID: <code>{valid_id}</code>) added.</blockquote></b>\n"

        await pro.edit(f"<b>✅ Admin(s) added successfully:</b>\n\n{admin_list}", reply_markup=reply_markup)

    except Exception as e:
        await pro.edit(f"<b>❌ Error occurred:</b> <code>{str(e)}</code>", reply_markup=reply_markup)


@Bot.on_message(filters.command('deladmin') & filters.private & filters.user(OWNER_ID))
async def delete_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    try:
        admin_ids = await db.get_all_admins() or []
        admins = message.text.split()[1:]

        if not admins:
            return await pro.edit(
                "<b>Please provide valid admin ID(s) to remove.</b>\n\n"
                "<b>Usage:</b>\n"
                "<code>/deladmin [user_id]</code> — Remove specific IDs\n"
                "<code>/deladmin all</code> — Remove all admins",
                reply_markup=reply_markup
            )

        if len(admins) == 1 and admins[0].lower() == "all":
            if admin_ids:
                for admin_id in admin_ids:
                    await db.del_admin(admin_id)
                ids = "\n".join(f"<blockquote><code>{admin}</code> ✅</blockquote>" for admin in admin_ids)
                return await pro.edit(f"<b>⛔️ All admin IDs have been removed:</b>\n{ids}", reply_markup=reply_markup)
            else:
                return await pro.edit("<b><blockquote>No admin IDs to remove.</blockquote></b>", reply_markup=reply_markup)

        passed = ""
        for admin_id in admins:
            try:
                valid_id = int(admin_id)
            except ValueError:
                passed += f"<blockquote><b>Invalid ID: <code>{admin_id}</code></b></blockquote>\n"
                continue

            if valid_id in admin_ids:
                await db.del_admin(valid_id)
                passed += f"<blockquote><code>{valid_id}</code> ✅ Removed</blockquote>\n"
            else:
                passed += f"<blockquote><b>ID <code>{valid_id}</code> not found in admin list.</b></blockquote>\n"

        await pro.edit(f"<b>⛔️ Admin removal result:</b>\n\n{passed}", reply_markup=reply_markup)

    except Exception as e:
        await pro.edit(f"<b>❌ Error occurred:</b> <code>{str(e)}</code>", reply_markup=reply_markup)


@Bot.on_message(filters.command('admins') & filters.private & admin)
async def get_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    try:
        admin_ids = await db.get_all_admins() or []

        if not admin_ids:
            admin_list = "<b><blockquote>❌ No admins found.</blockquote></b>"
        else:
            admin_items = []
            for admin_id in admin_ids:
                try:
                    user = await client.get_users(admin_id)
                    first_name = user.first_name if user.first_name else "Admin"
                    admin_items.append(
                        f"<b><blockquote>👤 <a href='tg://user?id={admin_id}'>{first_name}</a> | ID: <code>{admin_id}</code></blockquote></b>"
                    )
                except Exception:
                    admin_items.append(
                        f"<b><blockquote>👤 <a href='tg://user?id={admin_id}'>Admin</a> | ID: <code>{admin_id}</code></blockquote></b>"
                    )
            admin_list = "\n".join(admin_items)

        await pro.edit(f"<b>⚡ Current Admin List:</b>\n\n{admin_list}", reply_markup=reply_markup)

    except Exception as e:
        await pro.edit(f"<b>❌ Error occurred:</b> <code>{str(e)}</code>", reply_markup=reply_markup)


# ================= PREMIUM COMMANDS =================

@Bot.on_message(filters.command('myplan') & filters.private)
async def check_plan_cmd(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    try:
        user_id = message.from_user.id
        status = await check_user_plan(user_id)
        await pro.edit(f"<b><blockquote>{status}</blockquote></b>", reply_markup=reply_markup)
    except Exception as e:
        await pro.edit(f"<b>❌ Error occurred:</b> <code>{str(e)}</code>", reply_markup=reply_markup)


@Bot.on_message(filters.command('addpremium') & filters.private & admin)
async def add_premium_user_command(client: Client, msg: Message):
    pro = await msg.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    if len(msg.command) != 4:
        return await pro.edit(
            "<b>Usage:</b> <code>/addpremium <user_id> <value> <unit></code>\n\n"
            "<b>Units:</b> <code>s</code> (sec), <code>m</code> (min), <code>h</code> (hours), <code>d</code> (days), <code>y</code> (years)\n\n"
            "<b>Example:</b> <code>/addpremium 123456789 1 d</code>",
            reply_markup=reply_markup
        )

    try:
        user_id = int(msg.command[1])
        value = int(msg.command[2])
        unit = msg.command[3].lower()

        expires = await add_premium(user_id, value, unit)

        await pro.edit(
            f"<b><blockquote>✅ Premium added successfully!\n\n👤 User ID: <code>{user_id}</code>\n⏱ Duration: {value}{unit}\n📅 Expires: <code>{expires}</code></blockquote></b>",
            reply_markup=reply_markup
        )

        try:
            await client.send_message(
                user_id,
                f"<b>🎉 Premium Activated!</b>\n\n<b>Duration:</b> {value}{unit}\n<b>Expires:</b> <code>{expires}</code>"
            )
        except Exception:
            pass

    except Exception as e:
        await pro.edit(f"<b>❌ Error occurred:</b> <code>{str(e)}</code>", reply_markup=reply_markup)


@Bot.on_message(filters.command('remove_premium') & filters.private & admin)
async def remove_premium_cmd(client: Client, msg: Message):
    pro = await msg.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    if len(msg.command) != 2:
        return await pro.edit(
            "<b>Usage:</b> <code>/remove_premium <user_id></code>\n\n"
            "<b>Example:</b> <code>/remove_premium 123456789</code>",
            reply_markup=reply_markup
        )

    try:
        user_id = int(msg.command[1])
        await remove_premium(user_id)
        await pro.edit(
            f"<b><blockquote>✅ Premium removed for User ID: <code>{user_id}</code></blockquote></b>",
            reply_markup=reply_markup
        )
    except ValueError:
        await pro.edit("<b><blockquote>❌ Invalid User ID provided.</blockquote></b>", reply_markup=reply_markup)
    except Exception as e:
        await pro.edit(f"<b>❌ Error occurred:</b> <code>{str(e)}</code>", reply_markup=reply_markup)

@Bot.on_message(filters.command('premium_users') & filters.private & admin)
async def list_premium(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    try:
        from datetime import datetime, timezone as dt_tz

        now_utc = datetime.now(dt_tz.utc)

        try:
            users_list = await collection.find({}).to_list(length=None)
        except Exception:
            try:
                users_list = await db.col.find({}).to_list(length=None)
            except Exception:
                users_list = await db.users.find({}).to_list(length=None)

        final = []

        def parse_exp_date(exp_data):
            if isinstance(exp_data, datetime):
                return exp_data
            if isinstance(exp_data, (int, float)):
                return datetime.fromtimestamp(exp_data, tz=dt_tz.utc)
            if isinstance(exp_data, str):
                clean_str = exp_data.replace(" UTC", "").strip()
                
                try:
                    return datetime.fromisoformat(clean_str)
                except Exception:
                    pass
                
                formats = [
                    "%d-%m-%Y %I:%M:%S %p",
                    "%d-%m-%Y %H:%M:%S",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %I:%M:%S %p",
                    "%d/%m/%Y %H:%M:%S",
                    "%d/%m/%Y %I:%M:%S %p",
                    "%d-%m-%Y",
                    "%Y-%m-%d"
                ]
                for fmt in formats:
                    try:
                        return datetime.strptime(clean_str, fmt)
                    except Exception:
                        pass
            return None

        for user in users_list:
            uid = user.get("user_id") or user.get("_id") or user.get("id")
            if not uid or str(uid) in ["ADMINS", "timer", "shortener"]:
                continue

            exp_data = (
                user.get("expiration_timestamp")
                or user.get("expire_date")
                or user.get("expires")
                or user.get("expiry")
                or user.get("expires_at")
            )

            if not exp_data:
                continue

            exp_dt = parse_exp_date(exp_data)
            if not exp_dt:
                continue

            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=dt_tz.utc)

            remain_seconds = (exp_dt - now_utc).total_seconds()

            if remain_seconds <= 0:
                try:
                    await collection.delete_one({"_id": user.get("_id")})
                except Exception:
                    pass
                continue

            days = int(remain_seconds // 86400)
            hours = int((remain_seconds % 86400) // 3600)
            minutes = int((remain_seconds % 3600) // 60)

            time_left = ""
            if days > 0:
                time_left += f"{days}d "
            if hours > 0 or days > 0:
                time_left += f"{hours}h "
            time_left += f"{minutes}m"

            try:
                u = await client.get_users(int(uid))
                first_name = u.first_name if u.first_name else "User"
                user_link = f"<a href='tg://user?id={uid}'>{first_name}</a>"
            except Exception:
                user_link = f"<a href='tg://user?id={uid}'>User</a>"

            final.append(
                f"<b><blockquote>👤 {user_link} | ID: <code>{uid}</code>\n⏳ Rem: {time_left}</blockquote></b>"
            )

        if not final:
            await pro.edit("<b><blockquote>❌ No active premium users found.</blockquote></b>", reply_markup=reply_markup)
        else:
            text = "<b>⚡ Active Premium Users List:</b>\n\n" + "\n".join(final)
            if len(text) > 4000:
                text = text[:3900] + "\n\n<b>...and more users</b>"
            await pro.edit(text, reply_markup=reply_markup)

    except Exception as e:
        await pro.edit(f"<b>❌ Error occurred:</b> <code>{str(e)}</code>", reply_markup=reply_markup)


@Bot.on_message(filters.command("count") & filters.private & admin)
async def count_cmd(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    try:
        c = await db.get_total_verify_count()
        await pro.edit(
            f"<b><blockquote>📊 Total Verified Tokens Today: <code>{c}</code></blockquote></b>",
            reply_markup=reply_markup
        )
    except Exception as e:
        await pro.edit(f"<b>❌ Error occurred:</b> <code>{str(e)}</code>", reply_markup=reply_markup)


@Bot.on_message(filters.command('commands') & filters.private & admin)
async def admin_cmd(client: Client, message: Message):
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("• Close •", callback_data="close")]])
    try:
        await message.reply(
            text=CMD_TXT,
            reply_markup=reply_markup,
            quote=True
        )
    except Exception as e:
        await message.reply(f"<b>❌ Error occurred:</b> <code>{str(e)}</code>", quote=True)

# ================= END =================
