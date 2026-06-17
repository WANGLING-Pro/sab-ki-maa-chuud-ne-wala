# ================= IMPORTS =================

import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

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

# ================= SHORT URL FUNCTION =================

async def short_url(client: Client, message: Message, base64_string):
    try:
        username = client.me.username if client.me.username else "botusername"
        prem_link = f"https://t.me/{username}?start=yu3elk{base64_string}7"
        short_link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, prem_link)

        buttons = [
            [
                InlineKeyboardButton(text="ᴅᴏᴡɴʟᴏᴀᴅ", url=short_link),
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
    except IndexError:
        pass
    except Exception as e:
        print(f"SHORT_URL ERROR = {e}")

# ================= FORCE SUB FUNCTION =================

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
                InlineKeyboardButton(text=f"ᴊᴏɪɴ {chat.title}", url=link)
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
        print(f"FSUB ERROR: {e}")
        try:
            await client.send_message(
                OWNER_ID,
                f"⚠️ FSUB ERROR:\n<code>{e}</code>"
            )
        except:
            pass

        try:
            await temp.edit(
                f"<blockquote expandable><b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ @I_am_nerev_die</i></b></blockquote>\n"
                f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
            )
        except:
            pass

# ================= START COMMAND =================

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    try: 
        print("DB TYPE =", type(db))

        user_id = message.from_user.id
        print(f"[START] User {user_id} triggered start command")

        # ✅ BAN CHECK
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
        await message.reply_text("✅ Ban check passed!")
        
    except Exception as e:
        print(f"[ERROR] Start command failed: {e}")
        import traceback
        traceback.print_exc()

    # ✅ Check Force Subscription
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    # File auto-delete time in seconds
    FILE_AUTO_DELETE = await db.get_del_timer()

    # Add user if not already present
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except:
            pass

    # Handle normal message flow
    text = message.text

    if len(text) > 7:
        # ================= PAYLOAD BLOCK =================
        ids = None
        base64_string = None
        sent_msgs = []  # ✅ INITIALIZE HERE

        try:
            basic = text.split(" ", 1)[1]
            payload = basic

            print(f"PAYLOAD RECEIVED = {payload}")

            # ✅ Shortener check - is_premium already checked above
            if not is_premium and user_id != OWNER_ID and not basic.startswith("yu3elk"):
                print(f"SHORTENER MODE TRIGGERED FOR USER {user_id}")
                await short_url(client, message, basic)
                return

            # Shortener bypass payload extraction
            if basic.startswith("yu3elk"):
                print("Shortener format detected")
                base64_string = basic[6:-1]  # 'yu3elk' aur '7' remove
            else:
                print("Normal payload format")
                base64_string = basic

            print(f"BASE64 STRING TO DECODE = {base64_string}")

            # Decode to get IDs
            ids = await decode(base64_string)
            print(f"DECODE SUCCESS - IDS = {ids}, TYPE = {type(ids)}")

            # Old code pattern - string split by "-"
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
            import traceback
            print(f"FULL TRACEBACK: {traceback.format_exc()}")
            return await message.reply(f"❌ Invalid Link or Format Error: {str(e)[:100]}")

        # Safety check
        if not ids:
            print("IDS IS EMPTY - RETURNING")
            return await message.reply("❌ Failed to decode payload - IDs are empty")

        # ================= FETCH MESSAGES =================

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
            import traceback
            print(f"FETCH ERROR TRACEBACK: {traceback.format_exc()}")
            try:
                await temp_msg.delete()
            except:
                pass
            return await message.reply(f"❌ File not found in Database\n\nError: {str(fetch_err)[:80]}")

        # Delete temp message
        try:
            await temp_msg.delete()
        except:
            pass

        # ================= SEND FILES =================

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
                    protect_content=PROTECT_CONTENT
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
                        protect_content=PROTECT_CONTENT
                    )
                    sent_msgs.append(s)
                except:
                    pass

            except:
                continue

        # ================= AUTO DELETE =================

        FILE_DEL = await db.get_del_timer()

        if FILE_DEL and FILE_DEL > 0 and sent_msgs:

            note = await message.reply(
                f"<b>File will be deleted in {get_exp_time(FILE_DEL)}</b>"
            )

            await asyncio.sleep(FILE_DEL)

            for s in sent_msgs:
                try:
                    await s.delete()
                except:
                    pass

            try:
                await note.edit("File deleted.")
            except:
                pass

    else:
        # ================= NORMAL START MESSAGE =================

        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("• ᴍᴏʀᴇ ᴄʜᴀɴɴᴇʟs •", url="https://t.me/P_World_81")],
                [
                    InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
                    InlineKeyboardButton('ʜᴇʟᴘ •', callback_data="help")
                ]
            ]
        )
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

# ================= PREMIUM COMMANDS =================

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

        await msg.reply(f"✅ Added premium for {user_id}\nExpires: {expires}")

        await client.send_message(
            user_id,
            f"🎉 Premium Activated!\nDuration: {value}{unit}\nExpires: {expires}"
        )

    except Exception as e:
        await msg.reply(f"❌ Error: {str(e)}")


@Bot.on_message(filters.command('remove_premium') & filters.private & admin)
async def remove_premium_cmd(client, msg):
    if len(msg.command) != 2:
        return await msg.reply("Usage: /remove_premium user_id")
    try:
        user = int(msg.command[1])
        await remove_premium(user)
        await msg.reply("✅ Removed.")
    except:
        await msg.reply("❌ Invalid ID")


@Bot.on_message(filters.command('premium_users') & filters.private & admin)
async def list_premium(client, message):
    from pytz import timezone
    
    ist = timezone("Asia/Kolkata")
    users = collection.find({})
    final = ["<b>Active Premium Users:</b>\n"]

    now = datetime.now(ist)

    async for user in users:
        uid = user["user_id"]
        exp = datetime.fromisoformat(user["expiration_timestamp"]).astimezone(ist)

        remain = exp - now
        if remain.total_seconds() <= 0:
            await collection.delete_one({"user_id": uid})
            continue

        try:
            u = await client.get_users(uid)
            d = f"{remain.days}d {remain.seconds//3600}h {(remain.seconds//60)%60}m"

            final.append(
                f"<code>{uid}</code> | @{u.username or 'N/A'} | {u.mention} | {d}\n"
            )
        except:
            pass

    if len(final) == 1:
        await message.reply("No active premium users")
    else:
        await message.reply("".join(final))


@Bot.on_message(filters.command("count") & filters.private & admin)
async def count_cmd(client, message):
    c = await db.get_total_verify_count()
    await message.reply(f"<b>Total Verified Tokens Today: {c}</b>")


@Bot.on_message(filters.command('commands') & filters.private & admin)
async def admin_cmd(client, message):
    await message.reply(
        text=CMD_TXT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("• Close •", callback_data="close")]]),
        quote=True
    )

# ================= END =================